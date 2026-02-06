import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

from curriculum_manager import CurriculumManager
from safe_runner import run_safe

def test_solvability():
    base_dir = os.path.join(os.getcwd(), 'curriculum')
    cm = CurriculumManager(base_dir)
    cm.load()
    
    print(f"Testing {len(cm.lessons)} lessons for solvability...")
    
    failed = []
    passed = 0
    
    for lesson in cm.lessons:
        # Skip if no solution file
        if not lesson.solution_code:
            print(f"⚠️  Skipping {lesson.slug} (No solution.py)")
            continue
            
        print(f"Testing {lesson.slug}...", end='', flush=True)
        
        result = run_safe(lesson.solution_code, lesson.validator_script, timeout=2.0)
        
        if result['is_valid']:
            print(" ✅")
            passed += 1
        else:
            print(" ❌")
            print(f"   Error: {result.get('error_message')}")
            print(f"   Stdout: {result.get('stdout')}")
            failed.append(lesson.slug)

    print("-" * 40)
    print(f"Total: {len(cm.lessons)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("Failed Lessons:")
        for f in failed:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("✅ All checkable lessons are solvable!")
        sys.exit(0)

if __name__ == "__main__":
    test_solvability()
