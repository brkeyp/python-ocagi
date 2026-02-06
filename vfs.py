# -*- coding: utf-8 -*-
"""
Virtual File System (VFS) for Python Course Simulator.
Allows safe, in-memory file operations for the sandbox environment.
"""

import io
import os
import errno

class MockFileHandle(io.StringIO):
    """
    Simulates a file handle (like the object returned by open()).
    """
    def __init__(self, fs, path, mode):
        self.fs = fs
        self.path = path
        self.mode = mode
        self._closed_flag = False
        
        # Determine initial content based on mode
        initial_content = ""
        
        if 'r' in mode:
            if path not in fs.files:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
            initial_content = fs.files[path]
            # If r+, we start at 0 but have content. 
            # StringIO initializes with content and position 0.
            
        elif 'w' in mode:
            # Truncate / Create
            fs.files[path] = ""
            initial_content = ""
            
        elif 'a' in mode:
            # Append - pointer at end
            if path in fs.files:
                initial_content = fs.files[path]
            else:
                initial_content = ""
        
        super().__init__(initial_content)
        
        if 'a' in mode:
            self.seek(0, io.SEEK_END)
        elif 'r' in mode:
             self.seek(0, io.SEEK_SET)

    @property
    def closed(self):
        return self._closed_flag

    def close(self):
        """
        Flushes buffer to the VFS storage on close.
        """
        if self._closed_flag:
            return
            
        # If writing mode, save content back to FS
        if 'w' in self.mode or 'a' in self.mode or '+' in self.mode:
            self.fs.files[self.path] = self.getvalue()
            
        super().close()
        self._closed_flag = True
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class MockFileSystem:
    """
    A simple in-memory file system.
    Stores files as path -> content strings.
    """
    def __init__(self):
        self.files = {} # Dict[str, str]

    def open(self, file, mode='r', encoding=None, errors=None, newline=None, closefd=True, opener=None):
        """
        Replacement for built-in open().
        """
        # Normalize simple modes for this simulator
        # We generally support 'r', 'w', 'a' and text mode ONLY.
        if 'b' in mode:
            raise NotImplementedError("Binary mode not supported in this simulator.")
            
        # Normalize path (remove ./ etc) - simplified
        path = str(file)
        
        return MockFileHandle(self, path, mode)

    def exists(self, path):
        return path in self.files

    def read_file(self, path):
        """Helper to read content directly."""
        return self.files.get(path)

    def write_file(self, path, content):
        """Helper to write content directly (setup)."""
        self.files[path] = content

    def remove(self, path):
        """Simulates os.remove"""
        if path not in self.files:
             raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        del self.files[path]
