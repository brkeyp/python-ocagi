# -*- coding: utf-8 -*-
"""
Tests for ui_footer module (FooterState and FooterRenderer).
"""
import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Mock curses before imports
sys.modules['curses'] = MagicMock()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui_footer import FooterState


class TestFooterState:
    """Tests for FooterState class."""
    
    def test_initial_state(self):
        """Test FooterState initializes with correct defaults."""
        state = FooterState()
        
        assert state.vao_progress == 0
        assert state.show_hint == False
        assert state.vao_expire == 0
    
    def test_set_vao_progress(self):
        """Test setting VAO progress levels."""
        state = FooterState()
        
        state.set_vao_progress(1)
        assert state.vao_progress == 1
        assert state.vao_expire > 0  # Should have expire timestamp
        
        state.set_vao_progress(2)
        assert state.vao_progress == 2
        
        state.set_vao_progress(3)
        assert state.vao_progress == 3
    
    def test_set_vao_progress_zero_clears_expire(self):
        """Test setting VAO progress to 0 clears expiry."""
        state = FooterState()
        
        state.set_vao_progress(1)
        assert state.vao_expire > 0
        
        state.set_vao_progress(0)
        assert state.vao_progress == 0
        assert state.vao_expire == 0
    
    def test_reset_vao(self):
        """Test reset_vao clears all VAO state."""
        state = FooterState()
        
        state.set_vao_progress(2)
        assert state.vao_progress == 2
        
        state.reset_vao()
        assert state.vao_progress == 0
        assert state.vao_expire == 0
    
    def test_check_expired_clears_old_progress(self):
        """Test check_expired resets progress after expiry."""
        state = FooterState()
        
        # Set progress with immediate expiry (in the past)
        state.vao_progress = 2
        state.vao_expire = time.time() - 1  # Already expired
        
        state.check_expired()
        
        assert state.vao_progress == 0
        assert state.vao_expire == 0
    
    def test_check_expired_keeps_valid_progress(self):
        """Test check_expired keeps progress that hasn't expired."""
        state = FooterState()
        
        # Set progress with future expiry
        state.vao_progress = 2
        state.vao_expire = time.time() + 100  # Far future
        
        state.check_expired()
        
        assert state.vao_progress == 2  # Should still be set
    
    def test_show_hint_toggle(self):
        """Test show_hint can be toggled."""
        state = FooterState()
        
        assert state.show_hint == False
        
        state.show_hint = True
        assert state.show_hint == True
        
        state.show_hint = False
        assert state.show_hint == False
