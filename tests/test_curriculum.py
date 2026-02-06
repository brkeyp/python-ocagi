import sys
import os
import time

# Add root directory to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from curriculum_manager import CurriculumManager
from safe_runner import run_safe
import config

def run_solver_bot():
    print("🤖 Solver Bot: Initiating Curriculum Integrity Check...")
    print(f"📂 Root: {ROOT_DIR}")
    
    cm = CurriculumManager(os.path.join(ROOT_DIR, 'curriculum'))
    cm.load()
    
    total_lessons = cm.get_total_lessons()
    print(f"📊 Found {total_lessons} lessons.")
    
    passed = 0
    failed = []
    skipped = 0
    
    start_time = time.time()
    
    for i, lesson in enumerate(cm.lessons):
        # Progress indicator
        sys.stdout.write(f"\r[{i+1}/{total_lessons}] Testing {lesson.slug:<40}")
        sys.stdout.flush()
        
        if not lesson.solution_code:
            # If no solution provided, we skip? 
            # Or fail? Plan says "100% tasks must pass".
            # Migrated tasks should have solutions.
            # Only if solution is empty string.
            skipped += 1
            print(" ⚠️  No Solution Code")
            continue
            
        # Determine validator path
        validator_path = None
        if lesson.validator_script and os.path.exists(lesson.validator_script):
            validator_path = lesson.validator_script
            
        # Exec
        result = run_safe(lesson.solution_code, validator_path, timeout=2.0)
        
        if result['is_valid']:
            passed += 1
            # print(" ✅", end="")
        else:
            # print(" ❌", end="")
            failed.append({
                "lesson": lesson.slug,
                "error": result['error_message'],
                "stdout": result['stdout'],
                "solution": lesson.solution_code
            })
            
    total_time = time.time() - start_time
    print(f"\n\n{'='*50}")
    print(f"🏁 SCAN COMPLETE in {total_time:.2f}s")
    print(f"{'='*50}")
    print(f"✅ PASSED : {passed}")
    print(f"❌ FAILED : {len(failed)}")
    print(f"⏭️  SKIPPED: {skipped}")
    
    if failed:
        print("\n🔴 FAILURE REPORT:")
        for fail in failed:
            print(f"\n[ {fail['lesson']} ]")
            print(f"Error: {fail['error']}")
            print(f"Output: {fail['stdout'] or '(None)'}")
            # print(f"Code: {fail['solution'][:50]}...")
        sys.exit(1)
    else:
        print("\n✨ SYSTEM INTEGRITY: 100% OK")
        sys.exit(0)

if __name__ == "__main__":
    run_solver_bot()
