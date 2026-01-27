# -*- coding: utf-8 -*-
import threading
import queue
import curses
import time

class InputCollector:
    """
    Runs a blocking getch() call in a separate thread and
    puts the results into a thread-safe Queue.
    """
    def __init__(self, stdscr):
        self.stdscr = stdscr
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
        # Note: The thread might still be blocked on getch(), but since it's a daemon,
        # it will die when the main program exits. 
        # We can't easily interrupt a blocking curses call from another thread.
        
    def _input_loop(self):
        """The actual loop running in the background thread."""
        while self.running.is_set():
            try:
                # Blocking call - this is what we want to isolate
                # Using get_wch() for unicode support if available
                try:
                    ch = self.stdscr.get_wch()
                except AttributeError:
                    ch = self.stdscr.getch()
                except curses.error:
                    # Timeout or other error
                    continue
                    
                if not self.running.is_set():
                    break
                    
                self.queue.put(ch)
                
            except Exception:
                # If something goes wrong, wait a bit to avoid busy loop
                time.sleep(0.1)

    def get_input(self, block=False, timeout=None):
        """
        Retrieves input from the queue.
        
        Args:
            block (bool): Whether to block waiting for input.
            timeout (float): Timeout in seconds if blocking.
            
        Returns:
            The character/code, or None if queue is empty.
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def empty(self):
        return self.queue.empty()
