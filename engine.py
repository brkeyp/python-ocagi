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
    # Optional fields for future use or internal tracking
    task_id: int = 0 
    
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
class ActionExit:
    """UI should exit the application."""
    exit_code: int = 0

@dataclasses.dataclass
class ActionCustomView:
    view_name: str

# --- DATA HELPERS ---

def get_default_progress():
    return {
        "current_step": 1,
        "completed_tasks": [],
        "skipped_tasks": [],
        "user_code": {},
        "highest_reached_id": 1
    }

def validate_progress_data(data):
    """Ensures progress data has the correct schema, migrating if necessary."""
    default = get_default_progress()
    if not isinstance(data, dict): return default
    
    # 1. Ensure keys exist
    for key, value in default.items():
        if key not in data:
            data[key] = value
            
    # 2. Schema Migration (completed -> completed_tasks)
    if "completed" in data and "completed_tasks" not in data:
        data["completed_tasks"] = data.pop("completed")
    if "skipped" in data and "skipped_tasks" not in data:
        data["skipped_tasks"] = data.pop("skipped")
        
    # 3. Type checks
    if not isinstance(data.get("completed_tasks"), list): data["completed_tasks"] = []
    if not isinstance(data.get("skipped_tasks"), list): data["skipped_tasks"] = []
    if not isinstance(data.get("user_code"), dict): data["user_code"] = {}
    
    # Enforce Integers
    try: data["current_step"] = int(data.get("current_step", 1))
    except: data["current_step"] = 1
    
    try: data["highest_reached_id"] = int(data.get("highest_reached_id", 1))
    except: data["highest_reached_id"] = 1
    
    return data

# --- SIMULATION ENGINE ---

class SimulationEngine:
    def __init__(self):
        # Define base directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.progress_file = os.path.join(self.base_dir, 'progress.json')
        self.progress_backup = os.path.join(self.base_dir, 'progress.backup.json')
        
        # Initialize Curriculum Manager
        from curriculum_manager import CurriculumManager
        self.cm = CurriculumManager(os.path.join(self.base_dir, 'curriculum'))
        self.cm.load()
        
        self.progress = self._load_progress()
        self.last_run_result = None

    def _load_progress(self) -> Dict:
        data = get_default_progress()
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                if os.path.exists(self.progress_backup):
                    try:
                        with open(self.progress_backup, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except: pass
        
        return validate_progress_data(data)

    def _save_progress(self):
        # Backup
        if os.path.exists(self.progress_file):
            try:
                import shutil
                shutil.copy2(self.progress_file, self.progress_backup)
            except: pass
            
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=4, ensure_ascii=False)
        except Exception as e:
            pass

    def _get_current_state_info(self):
        current_step_id = self.progress.get("current_step", 1)
        completed = self.progress.get("completed_tasks", [])
        skipped = self.progress.get("skipped_tasks", [])
        
        # Use CurriculumManager to get lesson
        step = self.cm.get_lesson_by_id(current_step_id)
        
        return self.progress, current_step_id, completed, skipped, step

    def get_next_action(self) -> Union[ActionRenderEditor, ActionRenderCelebration, ActionExit, ActionShowMessage]:
        progress, current_step_id, completed, skipped, step = self._get_current_state_info()
        
        if not step:
            # Celebration Screen
            has_skipped = len(skipped) > 0
            return ActionRenderCelebration(
                completed_count=len(completed),
                skipped_count=len(skipped),
                has_skipped=has_skipped
            )
        
        # Determine status
        is_completed = current_step_id in completed
        is_skipped = current_step_id in skipped
        task_status = "completed" if is_completed else ("skipped" if is_skipped else "pending")
        
        # Build Task Info String (Legacy Compat)
        status_badge = config.UI.BADGE_SUCCESS if is_completed else (config.UI.BADGE_SKIPPED if is_skipped else "")
        
        task_info = f"{config.UI.LABEL_SECTION} {step.category}\n"
        task_info += f"{config.UI.LABEL_TASK} {current_step_id}: {step.title}{status_badge}\n"
        task_info += f"\n{config.UI.LABEL_QUESTION} {step.description}"
            
        saved_code = progress.get("user_code", {}).get(str(current_step_id), "")
        
        return ActionRenderEditor(
            task_info=task_info,
            hint_text=step.hint,
            initial_code=saved_code,
            task_status=task_status,
            completed_count=len(completed),
            skipped_count=len(skipped),
            task_id=current_step_id
        )

    def process_input(self, user_input: Optional[str]) -> Any:
        progress, current_step_id, completed, skipped, step = self._get_current_state_info()
        
        # --- COMMAND HANDLING ---
        
        # 1. RESET
        if user_input == "RESET_ALL":
            self.progress = get_default_progress()
            self._save_progress()
            return ActionShowMessage("İLERLEME SIFIRLANDI", "Tüm ilerleme silindi.", "reset", wait_for_enter=False)
        
        # 2. DEV MESSAGE
        if user_input == "DEV_MESSAGE":
            return ActionCustomView("dev_message")

        # 3. NAVIGATION (PREV/NEXT)
        if user_input == "PREV_TASK":
            if current_step_id > 1:
                self.progress["current_step"] = current_step_id - 1
                self._save_progress()
            return self.get_next_action()
            
        if user_input == "NEXT_TASK":
            highest = self.progress.get("highest_reached_id", 1)
            # Allow next if completed or skipped or if strictly less than highest
            # Logic from old engine: allow if current < highest
            if current_step_id < highest:
                 self.progress["current_step"] = current_step_id + 1
                 self._save_progress()
            return self.get_next_action()

        if user_input == "GOTO_FIRST_SKIPPED":
            if skipped:
                self.progress["current_step"] = min(skipped)
                self._save_progress()
            return self.get_next_action()
            
        if user_input == "SHOW_SOLUTION":
             if step:
                 return ActionShowMessage("📖 ÇÖZÜM", f"\n{step.solution_code}\n", "solution")

        # 4. SKIP (Double Enter defined as None in UI)
        if user_input is None:
            if not step:
                return ActionExit()
                
            is_skipped = current_step_id in skipped
            msg_title = "📖 ÇÖZÜM (Daha önce atlanmış görev)" if is_skipped else "⏩ SORU ATLANDI"
            
            if not is_skipped:
                self.progress["skipped_tasks"].append(current_step_id)
                self.progress["current_step"] = current_step_id + 1
                if self.progress["current_step"] > self.progress.get("highest_reached_id", 0):
                     self.progress["highest_reached_id"] = self.progress["current_step"]
                self._save_progress()
            
            # Refresh step info for next action (not needed if we return message)
            # But the message needs the solution of the SKIPPED task (current_step_id)
            # step object is still valid for current_step_id
            
            return ActionShowMessage(
                title=msg_title,
                content=f"✅ Bu sorunun DOĞRU ÇÖZÜMÜ:\n\n{step.solution_code}\n",
                type="info",
                wait_for_enter=True
            )

        # --- CODE SUBMISSION HANDLING ---
        # If we are here, user_input is Code String (and not a command like NEXT_TASK)
        
        if step is None:
            return ActionShowMessage("HATA", "Geçersiz görev.", "error")

        # Save User Code
        self.progress["user_code"][str(current_step_id)] = user_input
        self._save_progress()
        
        # Execute Code
        from safe_runner import run_safe
        
        validator_path = step.validator_script if step.validator_script and os.path.exists(step.validator_script) else None
        
        result = run_safe(user_input, validator_path)
        self.last_run_result = result
        
        stdout_val = result["stdout"]
        is_valid = result["is_valid"]
        error_message = result["error_message"]
        
        if is_valid:
            if current_step_id not in completed:
                self.progress["completed_tasks"].append(current_step_id)
            if current_step_id in skipped:
                self.progress["skipped_tasks"].remove(current_step_id)
            
            self.progress["current_step"] = current_step_id + 1
            if self.progress["current_step"] > self.progress.get("highest_reached_id", 0):
                 self.progress["highest_reached_id"] = self.progress["current_step"]
            self._save_progress()
            
            msg = "Görev başarıyla tamamlandı."
            if stdout_val:
                msg += f"\nÇıktı:\n{stdout_val}"
            
            # Auto-advance handled by Controller if wait_for_enter is False?
            # Old engine: wait_for_enter=is_skipped (False if fresh success)
            # If fresh success, we want implicit continue?
            # Controller: if wait=False, sleep then loop.
            return ActionShowMessage("TEBRİKLER! DOĞRU CEVAP.", msg, "success", wait_for_enter=False)
        else:
            msg = error_message if error_message else "Sonuç beklendiği gibi değil."
            if stdout_val:
                msg += f"\nKod Çıktısı: {stdout_val}"
            
            return ActionShowMessage("HATA VEYA YANLIŞ CEVAP", msg, "error")
