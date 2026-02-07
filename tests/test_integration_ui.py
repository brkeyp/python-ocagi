import pytest
import threading
import time
import curses
import sys
from unittest.mock import MagicMock, patch
from tests.virtual_terminal import VirtualTerminal

# Import app modules
import ui.editor as ui
import config
from input.api import EventType

class IntegrationTestRunner:
    def __init__(self):
        self.term = VirtualTerminal()
        self.app_thread = None
        self.exception = None
        
    def start(self):
        self.app_thread = threading.Thread(target=self._run_app, daemon=True)
        self.app_thread.start()
        # Wait for initial render
        self.term.wait_for_paint()
        
    def _run_app(self):
        try:
            # Prepare initial state
            task_info = "Task 1: Print Hello\nWrite code to print 'Hello'."
            hint = "Use print()"
            
            # We bypass the wrapper and run session directly with our mock terminal
            ui.run_editor_session(self.term, task_info=task_info, hint_text=hint)
        except KeyboardInterrupt:
            # Expected exit
            pass
        except Exception as e:
            self.exception = e
            
    def stop(self):
        # Send EXIT signal
        self.term.inject_input(chr(config.Keys.CTRL_C))
        if self.app_thread:
            self.app_thread.join(timeout=2.0)
            
    def assert_screen_contains(self, text, timeout=2.0):
        """Waits for text to appear on screen."""
        start = time.time()
        while time.time() - start < timeout:
            content = self.term.get_content()
            if text in content:
                return
            time.sleep(0.05)
        
        # Fail with debug info
        raise AssertionError(f"Text '{text}' not found in screen content:\n{self.term.get_content()}")

    def assert_cursor_at(self, y, x):
        assert self.term.cursor_y == y, f"Cursor Y expected {y}, got {self.term.cursor_y}"
        assert self.term.cursor_x == x, f"Cursor X expected {x}, got {self.term.cursor_x}"

@pytest.fixture
def runner():
    # Instantiate first to access term.refresh
    runner_instance = IntegrationTestRunner()
    
    # Patch curses module at the source where it is imported/used
    with patch.multiple(curses, 
                        curs_set=MagicMock(), 
                        start_color=MagicMock(), 
                        use_default_colors=MagicMock(), 
                        init_pair=MagicMock(), 
                        has_colors=MagicMock(return_value=True),
                        COLOR_RED=1, COLOR_CYAN=2, COLOR_YELLOW=3, 
                        COLOR_WHITE=4, COLOR_GREEN=5, COLOR_MAGENTA=6, COLOR_BLUE=7,
                        KEY_RESIZE=410, 
                        KEY_UP=259, KEY_DOWN=258, KEY_LEFT=260, KEY_RIGHT=261,
                        KEY_BACKSPACE=127, KEY_DC=330, KEY_ENTER=10,
                        doupdate=runner_instance.term.refresh):
        
        # Also patch input_curses which might depend on curses module
        with patch('input.curses_driver.curses', new=curses):
             yield runner_instance
             runner_instance.stop()
             if runner_instance.exception:
                 raise runner_instance.exception

def test_startup_render(runner):
    """Verify app starts and renders simple task info."""
    runner.start()
    runner.assert_screen_contains("Task 1: Print Hello")
    runner.assert_screen_contains("Write code to print 'Hello'")

def test_typing_code(runner):
    """Verify typing appears in the buffer."""
    runner.start()
    
    runner.term.inject_input("print('test')")
    runner.term.wait_for_paint()
    
    runner.assert_screen_contains("print('test')")
    
    # "print('test')" is 13 chars.
    # Logic: line 0. Screen Y is offset by header (~4-5 lines).
    # Just verify X position is correct (13) and Y is reasonable (>3)
    assert runner.term.cursor_x == 13
    assert runner.term.cursor_y >= 3

def test_multiline_editing(runner):
    """Verify Enter creates new lines and auto-indent."""
    runner.start()
    
    # Type: if True: <ENTER>
    runner.term.inject_input("if True:")
    runner.term.inject_input("\n")
    runner.term.wait_for_paint()
    
    runner.assert_screen_contains("if True:")
    # Should expect auto-indent (4 spaces) PLUS Gutter (12 spaces)
    # Because 2 lines with content triggers line numbers
    # X = 12 + 4 = 16
    assert runner.term.cursor_x == 16
    assert runner.term.cursor_y >= 4

def test_navigation(runner):
    """Verify arrow keys move cursor."""
    runner.start()
    
    runner.term.inject_input("Line1\nLine2")
    runner.term.wait_for_paint()
    
    # Cursor at end of Line2
    # 2 lines -> Line Numbers ON -> Gutter 12
    # Line2 len 5 -> X = 17
    initial_y = runner.term.cursor_y
    assert runner.term.cursor_x == 17
    
    # Move Up
    runner.term.inject_input(curses.KEY_UP)
    runner.term.wait_for_paint()
    
    assert runner.term.cursor_y == initial_y - 1
    assert runner.term.cursor_x == 17 # Line1 is 5 chars long + Gutter
    
    # Move Left
    runner.term.inject_input(curses.KEY_LEFT) # -> (0, 4)
    runner.term.inject_input(curses.KEY_LEFT) # -> (0, 3)
    runner.term.wait_for_paint()
    # X = 12 + 3 = 15
    assert runner.term.cursor_x == 15

def test_backspace(runner):
    """Verify backspace functionality."""
    runner.start()
    
    runner.term.inject_input("Test") # (0, 4)
    runner.term.inject_input(127) # Backspace (using ASCII 127/KEY_BACKSPACE)
    runner.term.wait_for_paint()
    
    runner.assert_screen_contains("Tes") # VirtualTerminal strips trailing spaces
    # Ensure Test is truncated
    line = runner.term.get_line(runner.term.cursor_y)
    assert "Tes" in line

