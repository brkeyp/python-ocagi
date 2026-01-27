# -*- coding: utf-8 -*-
import curses
import config
from input_api import InputDriver, InputEvent, EventType

class CursesInputDriver(InputDriver):
    """
    Curses implementation of the InputDriver.
    Handles platform-specific keycodes (Windows Numpad),
    ESC sequences for navigation (Alt+Arrows), and basic key mapping.
    """
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._setup_numpad_map()
        
    def _setup_numpad_map(self):
        """Maps Windows specific Numpad keycodes to standard characters."""
        self.numpad_map = {
            config.Keys.WIN_PAD_ENTER: (EventType.ENTER, None),
            config.Keys.WIN_PAD_SLASH: (EventType.CHAR, '/'),
            config.Keys.WIN_PAD_STAR:  (EventType.CHAR, '*'),
            config.Keys.WIN_PAD_MINUS: (EventType.CHAR, '-'),
            config.Keys.WIN_PAD_PLUS:  (EventType.CHAR, '+'),
        }

    def get_event(self, timeout_ms: int = -1) -> InputEvent:
        """
        Waits for and returns the next semantic InputEvent.
        Handles:
        - Timeout (returns EventType.TIMEOUT)
        - Unicode characters
        - Special function keys
        - Escape sequences (Alt+Arrows)
        - Windows Numpad normalization
        """
        # Set timeout
        if timeout_ms < 0:
            self.stdscr.timeout(config.Timing.TIMEOUT_BLOCKING)
        else:
            self.stdscr.timeout(timeout_ms)
            
        try:
            # Try to get a unicode character first
            try:
                char = self.stdscr.get_wch()
            except AttributeError:
                # Fallback for platforms/versions without get_wch
                char = self.stdscr.getch()
            except curses.error:
                # Timeout occurred
                return InputEvent(EventType.TIMEOUT)
                
        except KeyboardInterrupt:
            # Ctrl+C is often caught here or in the loop wrapper
            return InputEvent(EventType.EXIT)
            
        # 1. Handle Timeout (getch returns -1 on timeout)
        if char == -1:
            return InputEvent(EventType.TIMEOUT)
            
        # 2. Type Detection
        is_char_str = isinstance(char, str)
        char_code = ord(char) if is_char_str else char
        
        # 3. Windows Native Alt+Key checks (PDCurses/Windows-Curses specific)
        if char_code == config.Keys.WIN_ALT_LEFT:
            return InputEvent(EventType.PREV_TASK)
        elif char_code == config.Keys.WIN_ALT_RIGHT:
            return InputEvent(EventType.NEXT_TASK)
        elif char_code == config.Keys.CTRL_C:
            return InputEvent(EventType.EXIT)
            
        # 4. Windows Numpad Normalization
        if not is_char_str and char_code in self.numpad_map:
            etype, val = self.numpad_map[char_code]
            return InputEvent(etype, val)

        # 5. ESC Sequence Handling
        if char_code == config.Keys.ESC:
            return self._handle_esc_sequence()
            
        # 6. Standard Key Mapping
        # Navigation
        if char_code == curses.KEY_UP:
            return InputEvent(EventType.UP)
        elif char_code == curses.KEY_DOWN:
            return InputEvent(EventType.DOWN)
        elif char_code == curses.KEY_LEFT:
            return InputEvent(EventType.LEFT)
        elif char_code == curses.KEY_RIGHT:
            return InputEvent(EventType.RIGHT)
            
        # Editing
        elif char_code in (curses.KEY_BACKSPACE, config.Keys.BACKSPACE_1, config.Keys.BACKSPACE_2):
            return InputEvent(EventType.BACKSPACE)
        elif char_code in (curses.KEY_DC, config.Keys.DELETE):
            return InputEvent(EventType.DELETE)
        elif char_code in (curses.KEY_ENTER, config.Keys.ENTER, config.Keys.RETURN):
            return InputEvent(EventType.ENTER)
        elif is_char_str and char in ('\n', '\r'):
            return InputEvent(EventType.ENTER)
            
        # 7. Character Input
        # Only accept printable characters
        # Check specific ASCII range for int codes, or just string status
        if is_char_str:
            if len(char) == 1 and ord(char) >= 32:
                 # Check for '?' hint shortcut
                 if char == '?':
                     return InputEvent(EventType.SHOW_HINT)
                 return InputEvent(EventType.CHAR, char)
        elif 32 <= char_code < 127:
             # Fallback for non-wch systems returning int for chars
             ch = chr(char_code)
             if ch == '?':
                 return InputEvent(EventType.SHOW_HINT)
             return InputEvent(EventType.CHAR, ch)
             
        # Unknown/Unmapped key
        return InputEvent(EventType.UNKNOWN, str(char_code))

    def _handle_esc_sequence(self) -> InputEvent:
        """
        Disambiguates ESC key presses.
        Could be:
        1. Just ESC key (User hit Esc) -> Return ESCAPE
        2. Start of Alt+Arrow sequence (ESC + [ + ...) -> Return PREV/NEXT_TASK
        3. Start of Alt+Key (ESC + key) -> Could be PREV/NEXT if mapped
        """
        # Set a very short timeout to peek at the next key
        # If user pressed ESC physically, no other key follows instantly.
        # If it's a sequence, the next bytes are already buffered or coming very fast.
        self.stdscr.timeout(config.Timing.TIMEOUT_QUICK) # 50ms
        
        try:
            next_char = self.stdscr.getch()
        except curses.error:
            next_char = -1
            
        # Restore blocking/previous timeout is handled by get_event on next call, 
        # but technically we are inside get_event so we don't need to reset stdscr yet.
        
        if next_char == -1:
            # Timeout -> It was just ESC
            return InputEvent(EventType.ESCAPE)
            
        # We have a next char.
        
        # 1. Check for standard CSI sequence start '['
        if next_char == 91: # '['
            # This is likely a control sequence like Arrow or modifier
            # We need to read more.
            try:
                seq_char = self.stdscr.getch()
                if seq_char == -1: 
                    # Incomplete sequence? Treat as Unknown for now or just ignore
                    return InputEvent(EventType.UNKNOWN)
                    
                # Handle Alt+Arrows (xterm style: 1;3D or just 1;3)
                if seq_char == 49: # '1'
                    # Expect ';3D' or similar
                    self.stdscr.getch() # swallow ';'
                    mod = self.stdscr.getch() # modifier (3 = Alt)
                    direction = self.stdscr.getch() # D=left, C=right
                    
                    if mod == 51: # Alt
                        if direction == 68: # D (Left)
                            return InputEvent(EventType.PREV_TASK)
                        elif direction == 67: # C (Right)
                            return InputEvent(EventType.NEXT_TASK)
                            
                # Direct sequences ESC [ D (Left) could be treated as Left, 
                # but usually that's just Key_Left which curses handles.
                # However, some terms send ESC [ D for Alt+Left? No, usually that's plain Left.
                # ui.py had:
                elif seq_char == 68: # D
                     return InputEvent(EventType.PREV_TASK) # ui.py mapped this to PREV
                elif seq_char == 67: # C
                     return InputEvent(EventType.NEXT_TASK)
                     
            except curses.error:
                pass
                
        # 2. Check for Alt+Arrow aliases (ESC + ArrowKey)
        # Note: curses.KEY_LEFT might be returned by getch() if it parses the sequence!
        # But here we called getch(), which returns raw codes usually unless setupterm is perfect.
        # However, curses *might* return a keycode if it recognizes the sequence.
        elif next_char == curses.KEY_LEFT:
             return InputEvent(EventType.PREV_TASK)
        elif next_char == curses.KEY_RIGHT:
             return InputEvent(EventType.NEXT_TASK)
             
        # 3. Check for MacOS Option+Arrow ( ESC + b / f )
        elif next_char == 98: # 'b' (Back word/Alt+Left)
             return InputEvent(EventType.PREV_TASK)
        elif next_char == 102: # 'f' (Forward word/Alt+Right)
             return InputEvent(EventType.NEXT_TASK)
             
        # 4. It wasn't a sequence we know.
        # It might be "ESC" then "v" (fast typing) or just random bits.
        # CRITICAL: We consumed 'next_char'. If we return ESCAPE, we lose 'v'.
        # We must Push Back 'next_char' so the next get_event call sees it.
        curses.ungetch(next_char)
        return InputEvent(EventType.ESCAPE)
