# -*- coding: utf-8 -*-
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Any

class EventType(Enum):
    # Navigation
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    
    # Editing
    BACKSPACE = auto()
    DELETE = auto()
    ENTER = auto()
    CHAR = auto() # Has value
    
    # System/App
    EXIT = auto() # Ctrl+C
    RESIZE = auto()
    RESET_ALL = auto() # Ctrl+R
    
    # Navigation Actions
    PREV_TASK = auto()
    NEXT_TASK = auto()
    
    # Special
    ESCAPE = auto()
    SHOW_HINT = auto() # '?'
    
    # Meta / No-op
    TIMEOUT = auto() # Nothing happened within timeout
    UNKNOWN = auto()

@dataclass
class InputEvent:
    type: EventType
    value: Optional[str] = None
    
    @property
    def is_navigation(self):
        return self.type in (EventType.UP, EventType.DOWN, EventType.LEFT, EventType.RIGHT)
    
    @property
    def is_editing(self):
        return self.type in (EventType.BACKSPACE, EventType.DELETE, EventType.ENTER, EventType.CHAR)

class InputDriver:
    """Abstract base class for input drivers."""
    
    def get_event(self, timeout_ms: int = -1) -> InputEvent:
        """Get the next input event. Subclasses must implement."""
        raise NotImplementedError
    
    def close(self):
        """Clean up resources. Subclasses should override if needed."""
        pass
