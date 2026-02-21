# -*- coding: utf-8 -*-
import curses
import config
from input.api import InputDriver, InputEvent, EventType
from input.threaded import InputCollector

class CursesInputDriver(InputDriver):
    """
    Curses implementation of the InputDriver using Threaded InputCollector.
    Handles platform-specific keycodes (Windows Numpad),
    ESC sequences for navigation (Alt+Arrows), and basic key mapping.
    """
    
    def __init__(self, stdscr, lock=None):
        self.stdscr = stdscr
        self._setup_numpad_map()
        
        # Initialize Threaded Input Collector with Lock
        self.collector = InputCollector(stdscr, lock=lock)
        self.collector.start()
        
        # Local pushback buffer (replaces curses.ungetch)
        self.pushback_buffer = []

    def _normalize_key_code(self, char) -> int:
        """
        Converts char (str or int) to a safe integer key code.
        Useful because curses.get_wch() returns strings for printable chars.
        """
        if char is None:
            return -1
        if isinstance(char, str):
            return ord(char)
        return char
        
    def close(self):
        """Stops the input collector thread."""
        if self.collector:
            self.collector.stop()

    def _setup_numpad_map(self):
        """Maps Windows specific Numpad keycodes to standard characters."""
        self.numpad_map = {
            config.Keys.WIN_PAD_ENTER: (EventType.ENTER, None),
            config.Keys.WIN_PAD_SLASH: (EventType.CHAR, '/'),
            config.Keys.WIN_PAD_STAR:  (EventType.CHAR, '*'),
            config.Keys.WIN_PAD_MINUS: (EventType.CHAR, '-'),
            config.Keys.WIN_PAD_PLUS:  (EventType.CHAR, '+'),
        }

    def _get_raw_input(self, timeout_ms: int):
        """
        Internal wrapper to get input from buffer or collector.
        Respects timeout_ms.
        """
        # 1. Check local buffer first
        if self.pushback_buffer:
            return self.pushback_buffer.pop(0)

        # 2. Check collector
        # Convert ms to seconds, handling negative (blocking)
        block = (timeout_ms < 0)
        timeout = (timeout_ms / 1000.0) if not block else None
        
        return self.collector.get_input(block=block, timeout=timeout)

    def _unget_raw_input(self, char):
        """Pushes char back to the front of the local buffer."""
        self.pushback_buffer.insert(0, char)

    def get_event(self, timeout_ms: int = -1) -> InputEvent:
        """
        Waits for and returns the next semantic InputEvent.
        """
        try:
            # Get char from collector (or buffer)
            char = self._get_raw_input(timeout_ms)
                
        except KeyboardInterrupt:
            return InputEvent(EventType.EXIT)
            
        # 1. Handle Timeout (None returned by collector)
        if char is None:
            return InputEvent(EventType.TIMEOUT)
            
        # 2. Type Detection & Normalization
        is_char_str = isinstance(char, str)
        char_code = self._normalize_key_code(char)
        
        # 3. Windows Native Alt+Key checks
        if char_code == config.Keys.WIN_ALT_LEFT:
            return InputEvent(EventType.PREV_TASK)
        elif char_code == config.Keys.WIN_ALT_RIGHT:
            return InputEvent(EventType.NEXT_TASK)
        elif char_code == config.Keys.CTRL_C:
            return InputEvent(EventType.EXIT)
        elif char_code == config.Keys.CTRL_R:
            return InputEvent(EventType.RESET_ALL)
            
        # 4. Windows Numpad Normalization
        if not is_char_str and char_code in self.numpad_map:
            etype, val = self.numpad_map[char_code]
            return InputEvent(etype, val)

        # 5. ESC Sequence Handling
        if char_code == config.Keys.ESC:
            return self._handle_esc_sequence()
            
        # 6. Standard Key Mapping
        if char_code == curses.KEY_RESIZE:
            return InputEvent(EventType.RESIZE)
        elif char_code == curses.KEY_F1:
            return InputEvent(EventType.SHOW_HINT)
            
        if char_code == curses.KEY_UP:
            return InputEvent(EventType.UP)
        elif char_code == curses.KEY_DOWN:
            return InputEvent(EventType.DOWN)
        elif char_code == curses.KEY_LEFT:
            return InputEvent(EventType.LEFT)
        elif char_code == curses.KEY_RIGHT:
            return InputEvent(EventType.RIGHT)
            
        elif char_code in (curses.KEY_BACKSPACE, config.Keys.BACKSPACE_1, config.Keys.BACKSPACE_2):
            return InputEvent(EventType.BACKSPACE)
        elif char_code in (curses.KEY_DC, config.Keys.DELETE):
            return InputEvent(EventType.DELETE)
        elif char_code in (curses.KEY_ENTER, config.Keys.ENTER, config.Keys.RETURN):
            return InputEvent(EventType.ENTER)
        elif is_char_str and char in ('\n', '\r'):
            return InputEvent(EventType.ENTER)
            
        # 7. Character Input
        if is_char_str:
            if len(char) == 1 and ord(char) >= 32:
                 return InputEvent(EventType.CHAR, char)
        elif 32 <= char_code < 127:
             ch = chr(char_code)
             return InputEvent(EventType.CHAR, ch)
             
        return InputEvent(EventType.UNKNOWN, str(char_code))

    def _handle_esc_sequence(self) -> InputEvent:
        """
        Disambiguates ESC key presses using threaded peek.
        """
        # Set a very short timeout to peek at the next key (50ms)
        # Using _get_raw_input with actual timeout logic of Queue
        
        next_char = self._get_raw_input(config.Timing.TIMEOUT_QUICK)
        
        if next_char is None:
            return InputEvent(EventType.ESCAPE)
            
        # We have a next char.
        next_code = self._normalize_key_code(next_char)
        
        # 1. Check for standard CSI sequence start '['
        if next_code == 91: # '['
             # Read more (blocking is fine here as sequence chars come together)
            seq_char = self._get_raw_input(config.Timing.TIMEOUT_QUICK) # Short timeout ok
            seq_code = self._normalize_key_code(seq_char)
            
            if seq_char is None: 
                return InputEvent(EventType.UNKNOWN)
                
            # Handle Alt+Arrows (xterm style: 1;3D or just 1;3)
            if seq_code == 49: # '1'
                # Expect ';3D' or similar
                self._get_raw_input(100) # swallow ';'
                mod = self._get_raw_input(100) # modifier (3 = Alt)
                
                direction_char = self._get_raw_input(100) # D=left, C=right
                direction = self._normalize_key_code(direction_char)
                
                mod_code = self._normalize_key_code(mod)
                
                if mod_code == 51: # Alt
                    if direction == 68: # D (Left)
                        return InputEvent(EventType.PREV_TASK)
                    elif direction == 67: # C (Right)
                        return InputEvent(EventType.NEXT_TASK)
                        
            elif seq_code == 68: # D
                 return InputEvent(EventType.PREV_TASK)
            elif seq_code == 67: # C
                 return InputEvent(EventType.NEXT_TASK)
                 
        # 2. Check for Alt+Arrow aliases (ESC + ArrowKey)
        elif next_code == curses.KEY_LEFT:
             return InputEvent(EventType.PREV_TASK)
        elif next_code == curses.KEY_RIGHT:
             return InputEvent(EventType.NEXT_TASK)
             
        # 3. Check for MacOS Option+Arrow ( ESC + b / f )
        elif next_code == 98: # 'b'
             return InputEvent(EventType.PREV_TASK)
        elif next_code == 102: # 'f'
             return InputEvent(EventType.NEXT_TASK)
             
        # 4. It wasn't a sequence we know.
        # Push Back 'next_char' to our local buffer
        self._unget_raw_input(next_char)
        return InputEvent(EventType.ESCAPE)
