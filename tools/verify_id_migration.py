import sys
import os
import shutil

# Local Import Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine import SimulationEngine, ActionRenderEditor

def run_test():
    print("TEST: Initializing Engine...")
    engine = SimulationEngine()
    
    # 1. State Check
    p, c_id, comp, skip, step = engine._get_current_state_info()
    print(f"Current ID: {c_id}")
    print(f"Step Title: {step.title if step else 'None'}")
    
    if not isinstance(c_id, str):
        print("FAIL: Current ID is not a UUID string.")
        return
        
    if len(c_id) != 36:
        print("FAIL: Current ID does not look like a UUID.")
        return

    # 2. Render Check
    action = engine.get_next_action()
    if isinstance(action, ActionRenderEditor):
        print("RENDER: Success")
        print(f"Task Info:\n{action.task_info}")
    else:
        print(f"RENDER: Unexpected action {type(action)}")
        
    print("TEST: Complete.")

if __name__ == "__main__":
    run_test()
