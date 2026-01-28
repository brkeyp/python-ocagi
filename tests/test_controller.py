import pytest
import controller
import curses
import engine
from unittest.mock import MagicMock, patch
import sys

# --- TERMINAL VALIDATION ---

def test_validate_terminal_size_ok():
    """Returns True if size is sufficient."""
    with patch('shutil.get_terminal_size', return_value=(80, 24)):
        assert controller.validate_terminal_size() is True

def test_validate_terminal_size_fail():
    """Returns False if size is too small."""
    # Mock input to avoid stuck wait
    with patch('shutil.get_terminal_size', return_value=(10, 10)), \
         patch('builtins.print'), \
         patch('builtins.input'):
        assert controller.validate_terminal_size() is False

# --- ACTION HANDLING ---

def test_handle_action_show_message(mock_curses):
    """Should suspend curses and print message."""
    stdscr = MagicMock()
    action = engine.ActionShowMessage(
        title="Test Title",
        content="Test Content",
        type="info",
        wait_for_enter=False
    )
    
    with patch('controller.suspend_curses') as mock_suspend, \
         patch('builtins.print') as mock_print, \
         patch('time.sleep'): # Skip delay
         
         controller.handle_action(stdscr, action)
         
         mock_suspend.assert_called_once()
         # Verify key parts printed
         # Note: print might be called multiple times.
         # We just ensure it didn't crash and tried to print logic.

def test_handle_action_exit():
    """Should exit system."""
    action = engine.ActionExit(exit_code=5)
    with pytest.raises(SystemExit) as excinfo:
        controller.handle_action(MagicMock(), action)
    assert excinfo.value.code == 5

def test_handle_action_none():
    """Should do nothing if action is None."""
    # If it crashes, test fails
    controller.handle_action(MagicMock(), None)

# --- LOOP TESTS ---

def test_run_controller_startup_error():
    """Should handle curses error during startup."""
    with patch('controller.validate_terminal_size', return_value=True), \
         patch('curses.wrapper', side_effect=curses.error("Test Error")), \
         patch('builtins.print'), \
         patch('builtins.input'), \
         patch('sys.exit') as mock_exit:
         
         controller.run_controller()
         
         # Should catch error and exit(1)
         mock_exit.assert_called_with(1)

def test_run_loop_exit(mock_curses):
    """Loop should break on ActionExit."""
    stdscr = MagicMock()
    
    # Mock engine to return Exit immediately
    with patch('engine.SimulationEngine') as MockEngine:
        instance = MockEngine.return_value
        instance.get_next_action.return_value = engine.ActionExit()
        
        controller.run_loop(stdscr)
        
        # verified it breaks loop
