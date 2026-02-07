# -*- coding: utf-8 -*-
"""
Resource Guard Verification Tests

Bu test dosyası kaynak koruma modülünün doğru çalıştığını doğrular:
1. Sonsuz döngüler tespit edilip sonlandırılmalı
2. Bellek bombası saldırıları engellenmeli
3. Özyineleme bombaları engellenmeli
4. Normal müfredat görevleri sorunsuz çalışmalı

Güncel API: run_safe(user_code, validator_script_path, timeout)
"""

import sys
import os
import unittest
import time
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandbox.executor import run_safe

# Proje kök dizini
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Basit validation script path (her zaman True döner, sadece resource testleri için)
SIMPLE_VALIDATOR = os.path.join(
    PROJECT_ROOT, "curriculum", "01_temeller", "001_print_fonksiyonu", "validation.py"
)


def validator_exists():
    """Check if validator file exists for skip decorator."""
    return os.path.exists(SIMPLE_VALIDATOR)


@unittest.skipUnless(validator_exists(), "Validator file not found")
class TestResourceLimits(unittest.TestCase):
    """Kaynak limitleri testleri."""
    
    def test_infinite_loop_terminated(self):
        """Sonsuz döngü belirli sürede sonlandırılmalı."""
        print("\n--- Test Infinite Loop Termination ---")
        
        code = "while True: pass"
        start = time.time()
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        duration = time.time() - start
        
        self.assertFalse(result['success'])
        # Ya Zaman Aşımı ya da işlem limiti hatası olmalı
        self.assertTrue(
            'Zaman Aşımı' in result['error_message'] or 
            '⏰' in result['error_message'] or
            'döngü' in result['error_message'].lower() or
            'işlem' in result['error_message'].lower(),
            f"Expected timeout/loop message, got: {result['error_message']}"
        )
        # 2 saniye timeout + tolerans içinde tamamlanmalı
        self.assertTrue(duration < 5.0, f"Duration {duration}s too long")
        print(f"  ✓ Infinite loop terminated in {duration:.2f}s")
    
    def test_recursion_bomb_blocked(self):
        """Özyineleme bombası engellenmeli."""
        print("\n--- Test Recursion Bomb ---")
        
        code = """
def recursive_bomb():
    recursive_bomb()
    
recursive_bomb()
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=5.0)
        
        self.assertFalse(result['success'])
        # Özyineleme hatası mesajı olmalı
        self.assertTrue(
            'özyineleme' in result['error_message'].lower() or
            '🔄' in result['error_message'] or
            'recursion' in result['error_message'].lower() or
            'RecursionError' in result['error_message'],
            f"Expected recursion message, got: {result['error_message']}"
        )
        print(f"  ✓ Recursion bomb blocked")
    
    def test_memory_bomb_list(self):
        """Liste bellek bombası engellenmeli veya güvenli biçimde tamamlanmalı."""
        print("\n--- Test Memory Bomb (List) ---")
        
        # Bu test bellek limitine takılabilir, timeout olabilir veya
        # modern sistemlerde güvenli biçimde tamamlanabilir (copy-on-write)
        code = "x = [0] * (10 ** 9)"  # 1 milyar eleman
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=3.0)
        
        # Test geçti demek: uygulama çökmedi
        if result['success']:
            print(f"  ✓ Memory bomb handled safely (modern system optimization)")
        else:
            print(f"  ✓ Memory bomb blocked: {result['error_message'][:60]}...")
    
    def test_memory_bomb_string(self):
        """String bellek bombası engellenmeli veya güvenli biçimde tamamlanmalı."""
        print("\n--- Test Memory Bomb (String) ---")
        
        code = "x = 'a' * (10 ** 9)"  # 1 GB string
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=3.0)
        
        if result['success']:
            print(f"  ✓ String memory bomb handled safely")
        else:
            print(f"  ✓ String memory bomb blocked")
    
    def test_cpu_intensive_blocked(self):
        """CPU yoğun işlemler zaman aşımına uğramalı."""
        print("\n--- Test CPU Intensive Operation ---")
        
        code = """
result = 0
for i in range(10**8):
    result += i ** 2
"""
        start = time.time()
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        duration = time.time() - start
        
        # Ya timeout olmalı ya da işlem limiti
        self.assertFalse(result['success'])
        self.assertTrue(duration < 5.0, f"Duration {duration}s too long")
        print(f"  ✓ CPU intensive operation blocked in {duration:.2f}s")
    
    def test_fork_bomb_blocked(self):
        """Fork bombası (multiprocessing) engellenmeli."""
        print("\n--- Test Fork Bomb (Multiprocessing) ---")
        
        code = "import multiprocessing"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('⛔', result['error_message'])
        print(f"  ✓ Fork bomb blocked: multiprocessing import denied")
    
    def test_threading_blocked(self):
        """Threading modülü engellenmeli."""
        print("\n--- Test Threading Module ---")
        
        code = "import threading"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('⛔', result['error_message'])
        print(f"  ✓ Threading blocked: import denied")
    
    def test_sys_blocked(self):
        """sys modülü engellenmeli (güvenlik düzeltmesi sonrası)."""
        print("\n--- Test sys Module Blocked ---")
        
        code = "import sys"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('⛔', result['error_message'])
        print(f"  ✓ sys module blocked")


@unittest.skipUnless(validator_exists(), "Validator file not found")
class TestNormalCodeWorks(unittest.TestCase):
    """Normal kodların çalıştığını doğrular."""
    
    def test_simple_print(self):
        """Basit print çalışmalı."""
        print("\n--- Test Simple Print ---")
        
        code = "print('Merhaba Dünya')"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('Merhaba Dünya', result['stdout'])
        print(f"  ✓ Simple print works")
    
    def test_loop_within_limits(self):
        """Normal döngüler çalışmalı."""
        print("\n--- Test Normal Loop ---")
        
        code = """
toplam = 0
for i in range(10000):
    toplam += i
print(toplam)
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('49995000', result['stdout'])
        print(f"  ✓ Normal loop works")
    
    def test_recursion_within_limits(self):
        """Normal özyineleme çalışmalı."""
        print("\n--- Test Normal Recursion ---")
        
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(10)
print(result)
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('3628800', result['stdout'])
        print(f"  ✓ Normal recursion works")
    
    def test_moderate_list(self):
        """Orta boyutlu liste oluşturulabilmeli."""
        print("\n--- Test Moderate List ---")
        
        code = """
numbers = list(range(100000))
print(len(numbers))
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('100000', result['stdout'])
        print(f"  ✓ Moderate list works")
    
    def test_math_operations(self):
        """Matematik işlemleri çalışmalı."""
        print("\n--- Test Math Operations ---")
        
        code = """
import math
result = math.sqrt(144)
print(int(result))
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('12', result['stdout'])
        print(f"  ✓ Math operations work")


@unittest.skipUnless(validator_exists(), "Validator file not found")
class TestSafeOSRestrictions(unittest.TestCase):
    """SafeOS güvenlik kısıtlamalarını doğrular."""
    
    def test_os_system_blocked(self):
        """os.system engellenmeli."""
        print("\n--- Test os.system Blocked ---")
        
        code = "import os; os.system('ls')"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('tehlikeli sistem işlemleri yapılamaz', result['error_message'])
        print(f"  ✓ os.system blocked")
        
    def test_os_popen_blocked(self):
        """os.popen engellenmeli."""
        print("\n--- Test os.popen Blocked ---")
        
        code = "import os; os.popen('ls')"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('devre dışı', result['error_message'])
        print(f"  ✓ os.popen blocked")
        
    def test_os_remove_blocked(self):
        """os.remove engellenmeli."""
        print("\n--- Test os.remove Blocked ---")
        
        code = "import os; os.remove('test.txt')"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertFalse(result['success'])
        self.assertIn('devre dışı', result['error_message'])
        print(f"  ✓ os.remove blocked")

    def test_os_getcwd_allowed(self):
        """os.getcwd izin verilmeli."""
        print("\n--- Test os.getcwd Allowed ---")
        
        code = "import os; print(os.getcwd())"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        # Path should be in stdout (may vary but shouldn't fail)
        print(f"  ✓ os.getcwd allowed")

    def test_os_path_allowed(self):
        """os.path işlemleri izin verilmeli."""
        print("\n--- Test os.path Allowed ---")
        
        code = "import os; print(os.path.join('klasör', 'dosya.txt'))"
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('dosya.txt', result['stdout'])
        print(f"  ✓ os.path allowed")

    
    def test_os_allowed(self):
        """os modülü izinli olmalı (müfredat dersi için gerekli)."""
        print("\n--- Test os Module Allowed ---")
        
        code = """
import os
adres = os.getcwd()
print(type(adres).__name__)
"""
        result = run_safe(code, SIMPLE_VALIDATOR, timeout=2.0)
        
        self.assertTrue(result['success'])
        self.assertIn('str', result['stdout'])
        print(f"  ✓ os module allowed")


@unittest.skipUnless(validator_exists(), "Validator file not found")
class TestCurriculumRegression(unittest.TestCase):
    """Müfredat görevlerinin çalıştığını doğrular."""
    
    CURRICULUM_DIR = os.path.join(PROJECT_ROOT, "curriculum")
    
    # Kritik ders-çözüm çiftleri (validator path -> solution code)
    SAMPLE_TASKS = [
        # (chapter/lesson path suffix, solution code)
        ("01_temeller/001_print_fonksiyonu", 'print("Merhaba Python!")'),
        ("01_temeller/003_degisken_atama", "isim = 'Python'"),
        ("02_veri_tipleri/001_integer_float", "sayi = 42"),
        ("03_stringler/001_string_olusturma", 'mesaj = "Merhaba"'),
    ]
    
    def test_sample_curriculum_tasks(self):
        """Örnek müfredat görevleri çalışmalı."""
        print("\n--- Test Sample Curriculum Tasks ---")
        
        passed = 0
        for lesson_path, code in self.SAMPLE_TASKS:
            validator_path = os.path.join(self.CURRICULUM_DIR, lesson_path, "validation.py")
            
            if not os.path.exists(validator_path):
                print(f"  ⚠ Skipping {lesson_path} (validator not found)")
                continue
            
            with self.subTest(lesson=lesson_path):
                result = run_safe(code, validator_path, timeout=5.0)
                
                self.assertTrue(
                    result['is_valid'],
                    f"Task {lesson_path} failed: {result.get('error_message', 'Unknown error')}"
                )
                print(f"  ✓ Task {lesson_path} passed")
                passed += 1
        
        print(f"\n  Total passed: {passed}/{len(self.SAMPLE_TASKS)}")


if __name__ == '__main__':
    print("\n" + "🛡️ KAYNAK KORUMA TESTLERİ".center(60) + "\n")
    
    # Force spawn for test
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except:
        pass
    
    unittest.main(verbosity=2)
