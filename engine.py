import json
import os
import time
import dataclasses
from typing import Optional, List, Dict, Any, Union
import config

# --- EVENTS / ACTIONS ---

@dataclasses.dataclass
class ActionRenderEditor:
    """UI should render the code editor."""
    task_info: str
    hint_text: str
    initial_code: str
    task_status: str  # 'pending', 'completed', 'skipped'
    completed_count: int
    skipped_count: int
   
@dataclasses.dataclass
class ActionRenderCelebration:
    """UI should render the celebration screen."""
    completed_count: int
    skipped_count: int
    has_skipped: bool

@dataclasses.dataclass
class ActionShowMessage:
    """UI should suspend curses and show a message."""
    title: str
    content: str
    type: str  # 'success', 'error', 'info', 'solution', 'reset'
    wait_for_enter: bool = True
    clear_screen: bool = True

@dataclasses.dataclass
class ActionCustomView:
    """UI should suspend/handle a custom view."""
    view_name: str  # e.g., 'dev_message'

@dataclasses.dataclass
class ActionExit:
    """UI should exit the application."""
    exit_code: int = 0

# --- DATA & HELPERS ---

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CURRICULUM_FILE = os.path.join(DATA_DIR, config.System.FILENAME_CURRICULUM)
PROGRESS_FILE = os.path.join(DATA_DIR, config.System.FILENAME_PROGRESS)
PROGRESS_BACKUP_FILE = os.path.join(DATA_DIR, config.System.FILENAME_PROGRESS_BACKUP)

def load_curriculum():
    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_default_progress():
    return {
        "current_step_id": 1,
        "highest_reached_id": 1,
        "user_codes": {},
        "completed_tasks": [],
        "skipped_tasks": []
    }

def validate_progress_data(data):
    default = get_default_progress()
    if not isinstance(data, dict): return default
    for key, value in default.items():
        if key not in data: data[key] = value
    
    if not isinstance(data.get("current_step_id"), int) or data["current_step_id"] < 1:
        data["current_step_id"] = 1
    
    if not isinstance(data.get("highest_reached_id"), int) or data["highest_reached_id"] < 1:
        data["highest_reached_id"] = data["current_step_id"]
    
    if data["highest_reached_id"] < data["current_step_id"]:
        data["highest_reached_id"] = data["current_step_id"]
        
    if not isinstance(data.get("user_codes"), dict): data["user_codes"] = {}
    if not isinstance(data.get("completed_tasks"), list): data["completed_tasks"] = []
    if not isinstance(data.get("skipped_tasks"), list): data["skipped_tasks"] = []
    
    return data

def load_progress():
    default = get_default_progress()
    # Try main file
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return validate_progress_data(json.load(f))
        except (json.JSONDecodeError, IOError, OSError):
            pass
    # Try backup
    if os.path.exists(PROGRESS_BACKUP_FILE):
        try:
            with open(PROGRESS_BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = validate_progress_data(json.load(f))
            save_progress_data(data) # Restore main
            return data
        except (json.JSONDecodeError, IOError, OSError):
            pass
    return default

def save_progress_data(progress_data):
    # Backup existing
    if os.path.exists(PROGRESS_FILE):
        try:
            import shutil
            shutil.copy2(PROGRESS_FILE, PROGRESS_BACKUP_FILE)
        except (IOError, OSError): pass
    
    # Atomic write
    temp_file = PROGRESS_FILE + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, PROGRESS_FILE)
    except (IOError, OSError) as e:
        if os.path.exists(temp_file):
            try: os.remove(temp_file)
            except OSError: pass

def save_progress_field(field, value):
    progress = load_progress()
    progress[field] = value
    save_progress_data(progress)

def save_user_code(step_id, code):
    progress = load_progress()
    progress["user_codes"][str(step_id)] = code
    save_progress_data(progress)

def get_user_code(step_id):
    progress = load_progress()
    return progress.get("user_codes", {}).get(str(step_id), "")

def mark_task_completed(step_id):
    progress = load_progress()
    if step_id not in progress["completed_tasks"]:
        progress["completed_tasks"].append(step_id)
    if step_id in progress["skipped_tasks"]:
        progress["skipped_tasks"].remove(step_id)
    save_progress_data(progress)

def mark_task_skipped(step_id):
    progress = load_progress()
    if step_id not in progress["skipped_tasks"]:
        progress["skipped_tasks"].append(step_id)
    save_progress_data(progress)

def reset_all_progress():
    save_progress_data(get_default_progress())

# --- SIMULATION ENGINE ---

class SimulationEngine:
    def __init__(self):
        self.curriculum = load_curriculum()
        self.last_action = None
        
    def _get_current_state_info(self):
        progress = load_progress()
        current_step_id = progress.get("current_step_id", 1)
        completed = progress.get("completed_tasks", [])
        skipped = progress.get("skipped_tasks", [])
        
        step = next((item for item in self.curriculum if item["id"] == current_step_id), None)
        return progress, current_step_id, completed, skipped, step

    def get_next_action(self) -> Union[ActionRenderEditor, ActionRenderCelebration]:
        """Determines the initial UI state (Editor or Celebration)."""
        progress, current_step_id, completed, skipped, step = self._get_current_state_info()
        
        if not step:
            # Celebration Screen
            has_skipped = len(skipped) > 0
            return ActionRenderCelebration(
                completed_count=len(completed),
                skipped_count=len(skipped),
                has_skipped=has_skipped
            )
        
        # Determine Task Status
        is_completed = current_step_id in completed
        is_skipped = current_step_id in skipped
        task_status = "completed" if is_completed else ("skipped" if is_skipped else "pending")
        
        # Prepare Task Output
        status_badge = config.UI.BADGE_SUCCESS if is_completed else (config.UI.BADGE_SKIPPED if is_skipped else "")
        
        task_info = f"{config.UI.LABEL_SECTION} {step['cat']}\n"
        raw_task = step['task']
        if '\n' in raw_task:
            title_line, desc_part = raw_task.split('\n', 1)
            # Try to clean up "1. Title" format
            if title_line.strip().startswith(str(step['id']) + "."):
                try:
                     clean_title = title_line.split('.', 1)[1].strip().strip(':')
                     task_info += f"{config.UI.LABEL_TASK} {step['id']}: {clean_title}{status_badge}\n"
                except IndexError:
                     task_info += f"{config.UI.LABEL_TASK} {step['id']}: {title_line}{status_badge}\n"
            else:
                task_info += f"{config.UI.LABEL_TASK} {step['id']}: {title_line}{status_badge}\n"
            task_info += f"\n{config.UI.LABEL_QUESTION} {desc_part}"
        else:
            task_info += f"{config.UI.LABEL_TASK} {step['id']}:{status_badge}\n\n{config.UI.LABEL_QUESTION} {raw_task}"
            
        previous_code = get_user_code(current_step_id)
        
        return ActionRenderEditor(
            task_info=task_info,
            hint_text=step['hint'],
            initial_code=previous_code,
            task_status=task_status,
            completed_count=len(completed),
            skipped_count=len(skipped)
        )

    def process_input(self, user_input: Optional[str]) -> Any:
        """Processes input from the UI (Code or Commands) and returns the next Action."""
        
        progress, current_step_id, completed, skipped, step = self._get_current_state_info()
        
        # --- COMMAND HANDLING ---
        
        if user_input == "RESET_ALL":
            reset_all_progress()
            return ActionShowMessage(
                title="🗑️  İLERLEME SIFIRLANDI!",
                content="Yolculuğa en baştan başlıyoruz...",
                type="reset",
                wait_for_enter=False
            ) # Controller handles sleep
            
        if user_input == "DEV_MESSAGE":
            return ActionCustomView(view_name="dev_message")
            
        if user_input == "PREV_TASK":
            if current_step_id > 1:
                progress["current_step_id"] = current_step_id - 1
                save_progress_data(progress)
            return self.get_next_action()
            
        if user_input == "NEXT_TASK":
            highest_reached = progress.get("highest_reached_id", current_step_id)
            if current_step_id < highest_reached:
                progress["current_step_id"] = current_step_id + 1
                save_progress_data(progress)
            # If at the end, get_next_action handles it (returns celebration logic if step invalid?)
            # Wait, get_next_action checks step existence.
            return self.get_next_action()

        if user_input == "GOTO_FIRST_SKIPPED":
            if skipped:
                first_skipped = min(skipped)
                progress["current_step_id"] = first_skipped
                save_progress_data(progress)
            return self.get_next_action()
            
        if user_input == "SHOW_SOLUTION":
             # Should only happen if step exists
            if step:
                return ActionShowMessage(
                    title="📖 ÇÖZÜM",
                    content=f"\n{step['sol']}\n",
                    type="solution"
                )
            
        if user_input is None: # SKIPPED / ENTER on empty or Celebration
             # If celebration mode and None returned, it means Exit or just loop?
             # run_editor_session returns specific strings or code. 
             # If it returns None, it usually means SKIP (in Task mode).
             
             if not step:
                 # In celebration mode, None implies user quit or just Enter without command
                 # We treat it as Exit for safety or Loop?
                 # Loop: break -> exit. 
                 return ActionExit()
                 
             is_skipped = current_step_id in skipped
             
             # If skipped already, just show solution
             msg_title = "📖 ÇÖZÜM (Daha önce atlanmış görev)" if is_skipped else "⏩ SORU ATLANDI"
             
             # Update Logic
             if not is_skipped:
                 mark_task_skipped(current_step_id)
                 # Advance
                 progress = load_progress() # Refresh
                 progress["current_step_id"] = current_step_id + 1
                 save_progress_data(progress)
            
             return ActionShowMessage(
                 title=msg_title,
                 content=f"✅ Bu sorunun DOĞRU ÇÖZÜMÜ:\n\n{step['sol']}\n",
                 type="info",
                 wait_for_enter=True
             )

        # --- CODE SUBMISSION HANDLING ---
        
        # If we are here, user_input is the code string
        # 1. Save Code
        save_user_code(current_step_id, user_input)
        
        # 2. Run Safe
        from safe_runner import run_safe
        result = run_safe(user_input, step['id'])
        
        stdout_val = result["stdout"]
        is_valid = result["is_valid"]
        error_message = result["error_message"]
        
        if is_valid:
            is_skipped = current_step_id in skipped
            
            # Logic Update
            if not is_skipped:
                mark_task_completed(current_step_id)
                progress = load_progress()
                progress["current_step_id"] = current_step_id + 1
                if progress["current_step_id"] > progress.get("highest_reached_id", 0):
                    progress["highest_reached_id"] = progress["current_step_id"]
                save_progress_data(progress)
            
            content = ""
            if stdout_val:
                content += f"\nKod Çıktısı:\n{stdout_val}\n"
            if is_skipped:
                 content += "\n📝 Not: Bu görev daha önce atlandığı için 'Atlandı' olarak kayıtlı kalacak."
            
            return ActionShowMessage(
                title="✅ TEBRİKLER! DOĞRU CEVAP.",
                content=content,
                type="success",
                wait_for_enter=is_skipped # If skipped, wait. If not, auto-advance (controller handles sleep)
            )
        else:
            content = f"Hata Detayı: {error_message}\n"
            if stdout_val:
                content += f"Kod Çıktısı: {stdout_val}"
            
            return ActionShowMessage(
                title="❌ HATA VEYA YANLIŞ CEVAP",
                content=content,
                type="error",
                wait_for_enter=True
            )
