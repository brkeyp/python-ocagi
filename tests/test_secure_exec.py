# -*- coding: utf-8 -*-
"""
Secure Execution Tests

Bu test dosyası sandbox ve safe_runner modüllerinin güvenli çalıştığını doğrular.
Güncel API: run_safe(user_code, validator_script_path, timeout)
"""
import sys
import os
import unittest
import time

# Add parent directory to path to import safe_runner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandbox.executor import run_safe

# Test için basit bir validation script path (ilk ders)
SAMPLE_VALIDATOR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "curriculum", "01_temeller", "001_print_fonksiyonu", "validation.py"
)


class TestSecureExecution(unittest.TestCase):
    
    @unittest.skipUnless(os.path.exists(SAMPLE_VALIDATOR_PATH), "Validator file not found")
    def test_basic_execution(self):
        """Test that basic code executes successfully."""
        print("\n--- Test Basic Execution ---")
        code = "print('Hello Test')"
        result = run_safe(code, SAMPLE_VALIDATOR_PATH, timeout=2.0)
        self.assertTrue(result['success'])
        self.assertIn("Hello Test", result['stdout'])

    @unittest.skipUnless(os.path.exists(SAMPLE_VALIDATOR_PATH), "Validator file not found")
    def test_validation_success(self):
        """Test that correct code passes validation."""
        print("\n--- Test Validation Success ---")
        # 001_print_fonksiyonu expects 'Merhaba Python!' in output
        code = 'print("Merhaba Python!")'
        result = run_safe(code, SAMPLE_VALIDATOR_PATH, timeout=2.0)
        self.assertTrue(result['success'])
        self.assertTrue(result['is_valid'])

    @unittest.skipUnless(os.path.exists(SAMPLE_VALIDATOR_PATH), "Validator file not found")
    def test_syntax_error(self):
        """Test that syntax errors are caught."""
        print("\n--- Test Syntax Error ---")
        code = "print('Unclosed string"
        result = run_safe(code, SAMPLE_VALIDATOR_PATH, timeout=2.0)
        self.assertFalse(result['success'])
        # Error message should contain something about syntax
        self.assertTrue(
            "Yazım Hatası" in result['error_message'] or 
            "SyntaxError" in result['error_message'] or
            "Hata" in result['error_message']
        )

    @unittest.skipUnless(os.path.exists(SAMPLE_VALIDATOR_PATH), "Validator file not found")
    def test_blocked_module(self):
        """Test that dangerous modules are blocked."""
        print("\n--- Test Blocked Module ---")
        # sys module is now removed from ALLOWED_MODULES
        code = "import sys"
        result = run_safe(code, SAMPLE_VALIDATOR_PATH, timeout=2.0)
        self.assertFalse(result['success'])
        # Should have security error
        self.assertTrue("⛔" in result['error_message'] or "Güvenlik" in result['error_message'])

    @unittest.skipUnless(os.path.exists(SAMPLE_VALIDATOR_PATH), "Validator file not found")
    def test_timeout(self):
        """Test that infinite loops are terminated."""
        print("\n--- Test Timeout (Infinite Loop) ---")
        code = "while True: pass"
        start = time.time()
        result = run_safe(code, SAMPLE_VALIDATOR_PATH, timeout=1.0)
        duration = time.time() - start
        
        self.assertFalse(result['success'])
        # Error message could be timeout or operation limit exceeded
        self.assertTrue(
            "Zaman Aşımı" in result['error_message'] or 
            "işlem" in result['error_message'] or
            "⏰" in result['error_message']
        )
        # Should timeout within reasonable time (allow some margin for fast machines)
        self.assertTrue(0.1 < duration < 5.0, f"Duration {duration} not reasonable")


if __name__ == '__main__':
    # Force spawn for test
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except:
        pass
    unittest.main()
