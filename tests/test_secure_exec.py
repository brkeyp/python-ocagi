import sys
import os
import unittest
import time

# Add parent directory to path to import safe_runner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safe_runner import run_safe

class TestSecureExecution(unittest.TestCase):
    
    def test_basic_execution(self):
        print("\n--- Test Basic Execution ---")
        code = "print('Hello Test')"
        result = run_safe(code, step_id=1)
        self.assertTrue(result['success'])
        self.assertIn("Hello Test", result['stdout'])
        self.assertFalse(result['is_valid']) # Step 1 requires 'mesaj' var

    def test_validation_success(self):
        print("\n--- Test Validation Success ---")
        # Step 1 requires mesaj = "Merhaba Dünya"
        code = 'mesaj = "Merhaba Dünya"'
        result = run_safe(code, step_id=1)
        self.assertTrue(result['success'])
        self.assertTrue(result['is_valid'])

    def test_syntax_error(self):
        print("\n--- Test Syntax Error ---")
        code = "print('Unclosed string"
        result = run_safe(code, step_id=1)
        self.assertFalse(result['success'])
        self.assertIn("Yazım Hatası", result['error_message'])

    def test_system_exit(self):
        print("\n--- Test System Exit ---")
        code = "import sys; sys.exit(1)"
        result = run_safe(code, step_id=1)
        self.assertFalse(result['success'])
        self.assertIn("sys.exit", result['error_message'])

    def test_timeout(self):
        print("\n--- Test Timeout (Infinite Loop) ---")
        code = "while True: pass"
        start = time.time()
        result = run_safe(code, step_id=1, timeout=1.0) # 1s test override?
        # run_safe uses default 2.0 unless passed. Let's assume run_safe accepts timeout override or modify it.
        # My implementation of run_safe(user_code, step_id, timeout=2.0) allows override.
        duration = time.time() - start
        
        self.assertFalse(result['success'])
        self.assertIn("Zaman Aşımı", result['error_message'])
        # Tolerans
        self.assertTrue(0.9 < duration < 1.5, f"Duration {duration} not close to 1.0s")

if __name__ == '__main__':
    # Force spawn for test
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except:
        pass
    unittest.main()
