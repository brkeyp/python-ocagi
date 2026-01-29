# -*- coding: utf-8 -*-
import threading
import queue
import curses
import time

class InputCollector:
    """
    Runs a non-blocking getch() loop in a separate thread.
    Uses a Lock to ensure thread-safe access to stdscr.
    """
    def __init__(self, stdscr, lock=None):
        self.stdscr = stdscr
        # Use provided lock or create a new one (though sharing is best)
        self.lock = lock if lock else threading.Lock()
        
        self.queue = queue.Queue()
        self.running = threading.Event()
        self.thread = None
        
    def start(self):
        """Starts the input collection thread."""
        if self.thread is not None and self.thread.is_alive():
            return
            
        self.running.set()
        self.thread = threading.Thread(target=self._input_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stops the input collection thread."""
        self.running.clear()
        if self.thread:
            self.thread.join(timeout=0.2)
        
    def _input_loop(self):
        """The actual loop running in the background thread."""
        
        # Ensure we are in non-blocking mode for the polling loop
        # We need the lock to set this safely if main thread is drawing
        with self.lock:
             try:
                 self.stdscr.nodelay(True)
             except curses.error:
                 pass

        while self.running.is_set():
            try:
                # 1. Acquire Lock
                # We hold the lock ONLY while calling get_wch/getch
                # This prevents collision with renderer.refresh()
                char = None
                with self.lock:
                    try:
                        # Try to get a unicode character first
                        try:
                            char = self.stdscr.get_wch()
                        except AttributeError:
                            char = self.stdscr.getch()
                    except curses.error:
                        # Timeout/No Input in nodelay mode
                        char = None

                # 2. Process Result
                if char is not None and char != -1:
                    # Valid input
                    self.queue.put(char)
                else:
                    # No input, sleep to avoid busy loop
                    # 10ms sleep -> 100 Hz polling rate (plenty fast)
                    time.sleep(0.01)

            except Exception:
                # Fallback for unexpected thread errors - prevents input loop crash
                # Sleeping allows system to recover before next attempt
                time.sleep(0.1)

    def get_input(self, block=False, timeout=None):
        """
        Retrieves input from the queue.
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def empty(self):
        return self.queue.empty()
