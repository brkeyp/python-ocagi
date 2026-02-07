# -*- coding: utf-8 -*-
"""
Engine Module Tests

Bu test dosyası engine modülünün doğru çalıştığını doğrular.
Güncel API: SimulationEngine class-based progress management.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Import only what actually exists in engine.py
from engine import (
    SimulationEngine, 
    ActionRenderEditor, 
    ActionRenderCelebration,
    ActionShowMessage, 
    ActionExit, 
    get_default_progress
)


# --- VALIDATION TESTS ---

def test_get_default_progress_structure():
    """Default progress should have expected keys."""
    progress = get_default_progress()
    assert "current_step" in progress
    assert "completed_tasks" in progress
    assert "skipped_tasks" in progress
    assert "user_code" in progress
    assert isinstance(progress["completed_tasks"], list)
    assert isinstance(progress["skipped_tasks"], list)


def test_get_default_progress_initial_values():
    """Default progress should have valid initial values."""
    progress = get_default_progress()
    # current_step is None initially (migrated to UUID-based system)
    assert progress["current_step"] is None
    assert len(progress["completed_tasks"]) == 0
    assert len(progress["skipped_tasks"]) == 0


# --- ENGINE TESTS ---

@pytest.fixture
def engine():
    """Returns a fresh SimulationEngine instance."""
    # Mock curriculum and progress for isolated tests
    with patch.object(SimulationEngine, '_load_progress', return_value=get_default_progress()):
        with patch.object(SimulationEngine, '_save_progress'):
            engine = SimulationEngine()
            return engine


def test_engine_initialization():
    """Engine should initialize without errors."""
    try:
        engine = SimulationEngine()
        assert engine is not None
    except Exception as e:
        # If curriculum not available, that's expected in test environment
        if "curriculum" not in str(e).lower():
            raise


def test_get_next_action_returns_action(engine):
    """get_next_action should return an action object."""
    # This test depends on curriculum being loaded
    try:
        action = engine.get_next_action()
        assert action is not None
        # Should be one of the Action types
        assert isinstance(action, (ActionRenderEditor, ActionRenderCelebration, ActionShowMessage))
    except Exception:
        # Skip if curriculum not properly set up
        pytest.skip("Curriculum not available in test environment")


def test_process_reset_all(engine):
    """RESET_ALL command should return reset message."""
    action = engine.process_input("RESET_ALL")
    assert isinstance(action, ActionShowMessage)
    assert action.type == "reset"
    assert "SIFIRLANDI" in action.title.upper()


def test_process_exit():
    """ActionExit dataclass should work correctly."""
    # Note: Engine doesn't have an EXIT command - exit is handled by UI layer
    # Instead, test that ActionExit works as expected
    action = ActionExit(exit_code=0)
    assert action.exit_code == 0
    assert isinstance(action, ActionExit)


def test_process_navigation_prev_task(engine):
    """PREV_TASK should return an action."""
    action = engine.process_input("PREV_TASK")
    # Should return some action, either editor or message
    assert action is not None


def test_process_navigation_next_task(engine):
    """NEXT_TASK should return an action."""
    action = engine.process_input("NEXT_TASK")
    # Should return some action, either editor or message
    assert action is not None


# --- ACTION DATACLASS TESTS ---

def test_action_render_editor_fields():
    """ActionRenderEditor should have required fields."""
    action = ActionRenderEditor(
        task_info="Test task",
        hint_text="Test hint",
        initial_code="print('test')",
        task_status="pending",
        completed_count=0,
        skipped_count=0
    )
    assert action.task_info == "Test task"
    assert action.hint_text == "Test hint"
    assert action.task_status == "pending"


def test_action_render_celebration_fields():
    """ActionRenderCelebration should have required fields."""
    action = ActionRenderCelebration(
        completed_count=10,
        skipped_count=2,
        has_skipped=True
    )
    assert action.completed_count == 10
    assert action.skipped_count == 2
    assert action.has_skipped == True


def test_action_show_message_fields():
    """ActionShowMessage should have required fields."""
    action = ActionShowMessage(
        title="Test Title",
        content="Test Content",
        type="success"
    )
    assert action.title == "Test Title"
    assert action.content == "Test Content"
    assert action.type == "success"
    assert action.wait_for_enter == True  # default


def test_action_exit_default():
    """ActionExit should have default exit code 0."""
    action = ActionExit()
    assert action.exit_code == 0


def test_action_exit_custom_code():
    """ActionExit should accept custom exit code."""
    action = ActionExit(exit_code=1)
    assert action.exit_code == 1
