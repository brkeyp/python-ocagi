# -*- coding: utf-8 -*-
"""
Input Handling Tests

Bu test dosyası input modüllerinin doğru çalıştığını doğrular:
1. InputEvent dataclass yapısı
2. EventType enum değerleri
3. Temel input soyutlamaları

Güncel API:
- EventType: UP, DOWN, LEFT, RIGHT, BACKSPACE, DELETE, ENTER, CHAR, EXIT, RESIZE, 
             PREV_TASK, NEXT_TASK, ESCAPE, SHOW_HINT, TRIGGER_DEV_MESSAGE, TIMEOUT, UNKNOWN
- InputEvent: dataclass with type and value fields
"""

import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input_api import InputEvent, EventType, InputDriver


class TestEventType:
    """EventType enum testleri."""
    
    def test_has_char_event(self):
        """CHAR event tipi olmalı (karakter girişi)."""
        assert hasattr(EventType, 'CHAR')
    
    def test_has_enter_event(self):
        """ENTER event tipi olmalı."""
        assert hasattr(EventType, 'ENTER')
    
    def test_has_backspace_event(self):
        """BACKSPACE event tipi olmalı."""
        assert hasattr(EventType, 'BACKSPACE')
    
    def test_has_escape_event(self):
        """ESCAPE event tipi olmalı."""
        assert hasattr(EventType, 'ESCAPE')
    
    def test_has_navigation_events(self):
        """Navigasyon event tipleri olmalı (UP, DOWN, LEFT, RIGHT)."""
        assert hasattr(EventType, 'UP')
        assert hasattr(EventType, 'DOWN')
        assert hasattr(EventType, 'LEFT')
        assert hasattr(EventType, 'RIGHT')
    
    def test_has_timeout_event(self):
        """TIMEOUT event tipi olmalı."""
        assert hasattr(EventType, 'TIMEOUT')
    
    def test_has_exit_event(self):
        """EXIT event tipi olmalı (Ctrl+C)."""
        assert hasattr(EventType, 'EXIT')
    
    def test_has_task_navigation(self):
        """Görev navigasyon eventleri olmalı."""
        assert hasattr(EventType, 'PREV_TASK')
        assert hasattr(EventType, 'NEXT_TASK')
    
    def test_has_special_events(self):
        """Özel event tipleri olmalı."""
        assert hasattr(EventType, 'SHOW_HINT')
        assert hasattr(EventType, 'TRIGGER_DEV_MESSAGE')
        assert hasattr(EventType, 'UNKNOWN')
    
    def test_event_types_are_unique(self):
        """Event tipleri benzersiz olmalı."""
        types = [
            EventType.CHAR, EventType.ENTER, EventType.BACKSPACE,
            EventType.ESCAPE, EventType.UP, EventType.DOWN,
            EventType.LEFT, EventType.RIGHT, EventType.TIMEOUT,
            EventType.EXIT, EventType.PREV_TASK, EventType.NEXT_TASK
        ]
        assert len(types) == len(set(types))


class TestInputEvent:
    """InputEvent dataclass testleri."""
    
    def test_create_char_event(self):
        """CHAR event oluşturulabilmeli."""
        event = InputEvent(type=EventType.CHAR, value='a')
        assert event.type == EventType.CHAR
        assert event.value == 'a'
    
    def test_create_enter_event(self):
        """ENTER event oluşturulabilmeli."""
        event = InputEvent(type=EventType.ENTER)
        assert event.type == EventType.ENTER
    
    def test_create_navigation_event(self):
        """Navigation event oluşturulabilmeli."""
        event = InputEvent(type=EventType.UP)
        assert event.type == EventType.UP
    
    def test_create_timeout_event(self):
        """TIMEOUT event oluşturulabilmeli."""
        event = InputEvent(type=EventType.TIMEOUT)
        assert event.type == EventType.TIMEOUT
    
    def test_event_has_type_field(self):
        """Event type alanına sahip olmalı."""
        event = InputEvent(type=EventType.CHAR, value='x')
        assert hasattr(event, 'type')
    
    def test_event_has_value_field(self):
        """Event value alanına sahip olmalı."""
        event = InputEvent(type=EventType.CHAR, value='z')
        assert hasattr(event, 'value')
        assert event.value == 'z'
    
    def test_event_value_default_none(self):
        """Event value varsayılan olarak None olmalı."""
        event = InputEvent(type=EventType.ENTER)
        assert event.value is None
    
    def test_event_equality(self):
        """Aynı eventler eşit olmalı."""
        event1 = InputEvent(type=EventType.CHAR, value='a')
        event2 = InputEvent(type=EventType.CHAR, value='a')
        assert event1 == event2
    
    def test_event_inequality(self):
        """Farklı eventler eşit olmamalı."""
        event1 = InputEvent(type=EventType.CHAR, value='a')
        event2 = InputEvent(type=EventType.CHAR, value='b')
        assert event1 != event2
    
    def test_special_char_event(self):
        """Özel karakterler işlenebilmeli."""
        # Turkish characters
        event = InputEvent(type=EventType.CHAR, value='ğ')
        assert event.value == 'ğ'
        
        event2 = InputEvent(type=EventType.CHAR, value='ş')
        assert event2.value == 'ş'


class TestInputEventProperties:
    """InputEvent property testleri."""
    
    def test_is_navigation_for_up(self):
        """UP is_navigation True döndürmeli."""
        event = InputEvent(type=EventType.UP)
        assert event.is_navigation == True
    
    def test_is_navigation_for_down(self):
        """DOWN is_navigation True döndürmeli."""
        event = InputEvent(type=EventType.DOWN)
        assert event.is_navigation == True
    
    def test_is_navigation_for_char(self):
        """CHAR is_navigation False döndürmeli."""
        event = InputEvent(type=EventType.CHAR, value='a')
        assert event.is_navigation == False
    
    def test_is_editing_for_char(self):
        """CHAR is_editing True döndürmeli."""
        event = InputEvent(type=EventType.CHAR, value='a')
        assert event.is_editing == True
    
    def test_is_editing_for_backspace(self):
        """BACKSPACE is_editing True döndürmeli."""
        event = InputEvent(type=EventType.BACKSPACE)
        assert event.is_editing == True
    
    def test_is_editing_for_enter(self):
        """ENTER is_editing True döndürmeli."""
        event = InputEvent(type=EventType.ENTER)
        assert event.is_editing == True
    
    def test_is_editing_for_timeout(self):
        """TIMEOUT is_editing False döndürmeli."""
        event = InputEvent(type=EventType.TIMEOUT)
        assert event.is_editing == False


class TestInputDriver:
    """InputDriver abstract class testleri."""
    
    def test_input_driver_exists(self):
        """InputDriver sınıfı mevcut olmalı."""
        assert InputDriver is not None
    
    def test_input_driver_has_get_event(self):
        """InputDriver get_event metoduna sahip olmalı."""
        assert hasattr(InputDriver, 'get_event')
    
    def test_input_driver_get_event_raises_not_implemented(self):
        """get_event NotImplementedError fırlatmalı."""
        driver = InputDriver()
        with pytest.raises(NotImplementedError):
            driver.get_event()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
