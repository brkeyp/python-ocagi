import pytest
import json
import os
from engine import (
    validate_progress_data, load_progress, save_progress_data,
    SimulationEngine, ActionRenderEditor, ActionRenderCelebration,
    ActionShowMessage, ActionExit, get_default_progress,
    CURRICULUM_FILE, PROGRESS_FILE
)
from unittest.mock import patch, MagicMock

# --- VALIDATION TESTS ---

def test_validate_progress_data_defaults():
    """Ensure empty or invalid input returns defaults."""
    assert validate_progress_data(None) == get_default_progress()
    assert validate_progress_data({}) == get_default_progress()
    assert validate_progress_data("invalid") == get_default_progress()

def test_validate_progress_data_correction():
    """Ensure invalid values are corrected."""
    data = {
        "current_step_id": -5,
        "highest_reached_id": "invalid",
        "completed_tasks": "notalist",
        "skipped_tasks": None
    }
    fixed = validate_progress_data(data)
    assert fixed["current_step_id"] == 1
    assert fixed["highest_reached_id"] == 1
    assert isinstance(fixed["completed_tasks"], list)
    assert isinstance(fixed["skipped_tasks"], list)

def test_validate_progress_integrity():
    """Ensure highest_reached is never less than current."""
    data = {"current_step_id": 5, "highest_reached_id": 3}
    fixed = validate_progress_data(data)
    assert fixed["highest_reached_id"] == 5

# --- IO TESTS (MOCKED) ---

def test_load_progress_no_file(mock_fs):
    """Should return default if no file exists."""
    assert load_progress() == get_default_progress()

def test_load_progress_valid_file(mock_fs):
    """Should load valid json from file."""
    data = get_default_progress()
    data["current_step_id"] = 2
    mock_fs[PROGRESS_FILE] = json.dumps(data)
    
    loaded = load_progress()
    assert loaded["current_step_id"] == 2

def test_load_progress_corrupt_file(mock_fs):
    """Should return default if file is corrupt."""
    mock_fs[PROGRESS_FILE] = "{ invalid json"
    assert load_progress() == get_default_progress()

def test_save_progress_atomic(mock_fs):
    """Should write to temp and rename."""
    data = get_default_progress()
    data["current_step_id"] = 10
    
    save_progress_data(data)
    
    assert PROGRESS_FILE in mock_fs
    saved_data = json.loads(mock_fs[PROGRESS_FILE])
    assert saved_data["current_step_id"] == 10

# --- ENGINE LOGIC TESTS ---

@pytest.fixture
def engine_instance(mock_fs, sample_curriculum):
    """Returns an engine instance with a fresh environment."""
    return SimulationEngine()

def test_get_next_action_initial(engine_instance):
    """New user starts at step 1."""
    action = engine_instance.get_next_action()
    assert isinstance(action, ActionRenderEditor)
    assert action.task_status == "pending"
    assert "Merhaba Dünya" in action.task_info

def test_process_input_code_success(engine_instance, mock_fs):
    """Submitting correct code advances progress."""
    # Mock safe_runner to return success
    with patch("safe_runner.run_safe") as mock_runner:
        mock_runner.return_value = {"is_valid": True, "stdout": "Hola", "error_message": ""}
        
        # Action: Submit Code
        action = engine_instance.process_input("print('test')")
        
        # Expect Success Message
        assert isinstance(action, ActionShowMessage)
        assert action.type == "success"
        
        # Verify Progress Saved
        progress = json.loads(mock_fs[PROGRESS_FILE])
        assert progress["current_step_id"] == 2
        assert 1 in progress["completed_tasks"]

def test_process_input_code_fail(engine_instance):
    """Submitting wrong code shows error."""
    with patch("safe_runner.run_safe") as mock_runner:
        mock_runner.return_value = {"is_valid": False, "stdout": "", "error_message": "SyntaxError"}
        
        action = engine_instance.process_input("invalid code")
        
        assert isinstance(action, ActionShowMessage)
        assert action.type == "error"
        assert "SyntaxError" in action.content

def test_navigation_prev_next(engine_instance, mock_fs):
    """Test NEXT and PREV commands."""
    # Setup state: At step 1, but highest reached is 2
    data = get_default_progress()
    data["current_step_id"] = 1
    data["highest_reached_id"] = 2
    mock_fs[PROGRESS_FILE] = json.dumps(data)
    
    # Next (allowed because highest_reached >= 2)
    action = engine_instance.process_input("NEXT_TASK")
    assert isinstance(action, ActionRenderEditor)
    
    progress = json.loads(mock_fs[PROGRESS_FILE])
    assert progress["current_step_id"] == 2
    
    # Next again (blocked, max is 2)
    engine_instance.process_input("NEXT_TASK")
    progress = json.loads(mock_fs[PROGRESS_FILE])
    assert progress["current_step_id"] == 2 # Did not advance
    
    # Prev
    engine_instance.process_input("PREV_TASK")
    progress = json.loads(mock_fs[PROGRESS_FILE])
    assert progress["current_step_id"] == 1

def test_reset_all(engine_instance, mock_fs):
    """RESET_ALL should wipe progress."""
    data = get_default_progress()
    data["current_step_id"] = 5
    mock_fs[PROGRESS_FILE] = json.dumps(data)
    
    action = engine_instance.process_input("RESET_ALL")
    assert isinstance(action, ActionShowMessage)
    assert action.type == "reset"
    
    progress = json.loads(mock_fs[PROGRESS_FILE])
    assert progress["current_step_id"] == 1

def test_celebration_mode(engine_instance, mock_fs, sample_curriculum):
    """Should show celebration when all tasks done."""
    # Set current step to after last task
    last_id = sample_curriculum[-1]["id"]
    data = get_default_progress()
    data["current_step_id"] = last_id + 1
    mock_fs[PROGRESS_FILE] = json.dumps(data)
    
    action = engine_instance.get_next_action()
    assert isinstance(action, ActionRenderCelebration)

def test_skip_logic(engine_instance, mock_fs):
    """Skipping a task."""
    # Input None (Enter with empty code?? No, usually implies specific UI handling, 
    # but engine maps None to Skip if in editor)
    
    action = engine_instance.process_input(None)
    
    # Should show valid solution
    assert isinstance(action, ActionShowMessage)
    assert "SORU ATLANDI" in action.title or "ÇÖZÜM" in action.title
    assert "DOĞRU ÇÖZÜMÜ" in action.content
    
    # Progress Check
    progress = json.loads(mock_fs[PROGRESS_FILE])
    assert 1 in progress["skipped_tasks"]
    assert progress["current_step_id"] == 2
