# -*- coding: utf-8 -*-
"""
Tests for ui_utils module.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock curses before imports
sys.modules['curses'] = MagicMock()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.utils import OSUtils


class TestOSUtils:
    """Tests for OSUtils class."""
    
    def test_get_terminal_size_success(self):
        """Test get_terminal_size returns dimensions."""
        with patch('os.get_terminal_size', return_value=(120, 40)):
            cols, lines = OSUtils.get_terminal_size()
            
            assert cols == 120
            assert lines == 40
    
    def test_get_terminal_size_fallback(self):
        """Test get_terminal_size returns defaults on error."""
        with patch('os.get_terminal_size', side_effect=OSError):
            cols, lines = OSUtils.get_terminal_size()
            
            assert cols == 80
            assert lines == 24
    
    def test_clear_screen_unix(self):
        """Test clear_screen uses 'clear' on Unix."""
        with patch('os.name', 'posix'):
            with patch('os.system') as mock_system:
                OSUtils.clear_screen()
                mock_system.assert_called_once_with('clear')
    
    def test_clear_screen_windows(self):
        """Test clear_screen uses 'cls' on Windows."""
        with patch('os.name', 'nt'):
            with patch('os.system') as mock_system:
                OSUtils.clear_screen()
                mock_system.assert_called_once_with('cls')
    
    def test_resize_terminal(self):
        """Test resize_terminal writes ANSI escape sequence."""
        with patch('sys.stdout') as mock_stdout:
            OSUtils.resize_terminal(rows=30, cols=100)
            
            mock_stdout.write.assert_called_once()
            call_arg = mock_stdout.write.call_args[0][0]
            
            # Should contain ANSI resize sequence with rows and cols
            assert '30' in call_arg
            assert '100' in call_arg
            mock_stdout.flush.assert_called_once()
