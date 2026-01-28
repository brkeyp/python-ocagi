import curses
import threading
import time
import queue

class VirtualTerminal:
    """
    A comprehensive mock for curses stdscr to facilitate integration tests.
    Maintains an in-memory buffer of the screen content.
    """
    def __init__(self, rows=24, cols=80):
        self.rows = rows
        self.cols = cols
        
        # Screen Buffer: List of lists of characters
        self.screen = [[' ' for _ in range(cols)] for _ in range(rows)]
        # Attribute Buffer: List of lists of attributes
        self.attrs = [[0 for _ in range(cols)] for _ in range(rows)]
        
        self.cursor_y = 0
        self.cursor_x = 0
        
        # Input Queue for getch/get_wch
        self.input_queue = queue.Queue()
        
        # Synchronization for tests
        self.last_refresh_time = 0
        self._refresh_event = threading.Event()
        self.render_count = 0
        
        # Curses compatibility
        self.keypad_enabled = False
        self.nodelay_enabled = False

    # --- Inspection Methods (For Tests) ---
    
    def get_line(self, y):
        """Returns the string content of line y (stripped of trailing spaces)."""
        if 0 <= y < self.rows:
            return "".join(self.screen[y]).rstrip()
        return ""
        
    def get_content(self):
        """Returns full screen content as a single string."""
        return "\n".join("".join(row).rstrip() for row in self.screen)
    
    def wait_for_paint(self, timeout=1.0):
        """
        Blocks until the next refresh() call completes.
        Returns True if refresh happened, False on timeout.
        """
        self._refresh_event.clear()
        return self._refresh_event.wait(timeout)

    def inject_input(self, text_or_code):
        """
        Injects a string or keycode into the input queue.
        If string, injects each char individually.
        """
        if isinstance(text_or_code, str):
            for char in text_or_code:
                self.input_queue.put(char)
        else:
            self.input_queue.put(text_or_code)
            
    # --- Curses Methods (Mocked) ---
    
    def refresh(self):
        """Simulates screen refresh."""
        self.last_refresh_time = time.time()
        self.render_count += 1
        self._refresh_event.set()
        
    def erase(self):
        """Simulate erase (clear window)."""
        self.clear()

    def clear(self):
        for y in range(self.rows):
            for x in range(self.cols):
                self.screen[y][x] = ' '
                self.attrs[y][x] = 0
        self.cursor_y = 0
        self.cursor_x = 0
        
    def move(self, y, x):
        self.cursor_y = max(0, min(y, self.rows - 1))
        self.cursor_x = max(0, min(x, self.cols - 1))
        
    def addstr(self, *args):
        """
        Signatures:
        addstr(str)
        addstr(str, attr)
        addstr(y, x, str)
        addstr(y, x, str, attr)
        """
        y, x, text, attr = self._parse_addstr_args(args)
        
        # If y, x explicitly provided, move there
        if y is not None:
             self.cursor_y = y
             self.cursor_x = x
             
        for char in text:
            if char == '\n':
                self.cursor_y += 1
                self.cursor_x = 0
            elif char == '\r':
                self.cursor_x = 0
            else:
                if 0 <= self.cursor_y < self.rows and 0 <= self.cursor_x < self.cols:
                    self.screen[self.cursor_y][self.cursor_x] = char
                    self.attrs[self.cursor_y][self.cursor_x] = attr
                self.cursor_x += 1
                
                # Wrap
                if self.cursor_x >= self.cols:
                    self.cursor_y += 1
                    self.cursor_x = 0
                    
    def addch(self, *args):
        # Simply treat as addstr for now (simplified)
        y, x, ch, attr = self._parse_addstr_args(args)
        if isinstance(ch, int):
            ch = chr(ch)
        self.addstr(y, x, ch, attr)

    def chgat(self, *args):
        """
        chgat(y, x, num, attr)
        chgat(num, attr)
        """
        if len(args) == 2:
            num, attr = args
            y, x = self.cursor_y, self.cursor_x
        elif len(args) == 4:
            y, x, num, attr = args
        else:
            return

        if num == -1:
            num = self.cols - x
            
        for i in range(num):
            cx = x + i
            if 0 <= y < self.rows and 0 <= cx < self.cols:
                self.attrs[y][cx] = attr

    def get_wch(self):
        """Blocking or non-blocking get based on nodelay."""
        try:
            return self.input_queue.get(block=not self.nodelay_enabled, timeout=0.01 if self.nodelay_enabled else None)
        except queue.Empty:
            if self.nodelay_enabled:
                raise curses.error("no input")
            return None # Should not happen if blocking

    def getch(self):
        val = self.get_wch()
        if isinstance(val, str):
            return ord(val)
        return val

    def nodelay(self, flag):
        self.nodelay_enabled = flag
        
    def keypad(self, flag):
        self.keypad_enabled = flag

    def _parse_addstr_args(self, args):
        # Helper to parse overloaded arguments
        y, x, text, attr = None, None, "", 0
        if len(args) == 1:
            text = args[0]
        elif len(args) == 2:
             if isinstance(args[0], int): # y, x ? No, must be text, attr
                  text, attr = args
             else:
                  text, attr = args
        elif len(args) == 3:
            y, x, text = args
        elif len(args) == 4:
            y, x, text, attr = args
        return y, x, text, attr

    # Mock other used methods similarly
    def clrtoeol(self):
        for x in range(self.cursor_x, self.cols):
             self.screen[self.cursor_y][x] = ' '
             self.attrs[self.cursor_y][x] = 0

    def getyx(self):
        return self.cursor_y, self.cursor_x

    def getmaxyx(self):
        return self.rows, self.cols

    def noutrefresh(self):
        # In mock, we can arguably just mark as ready or do nothing 
        # as doupdate will trigger event.
        pass

    def border(self):
        pass # Simplified: do nothing

    def bkgd(self, ch, attr=0):
        pass

