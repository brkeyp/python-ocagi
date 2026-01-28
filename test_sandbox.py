"""
Sandbox Verification Tests

Bu test dosyası sandbox modülünün doğru çalıştığını doğrular:
1. Tüm 37 müfredat görevi çalışmalı
2. Tehlikeli işlemler engellenmiş olmalı
3. Hata mesajları Türkçe ve anlaşılır olmalı
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from safe_runner import run_safe

# =============================================================================
# MÜFREDAT GÖREVLERİ TEST KODLARI
# =============================================================================

CURRICULUM_TEST_CASES = {
    1: "mesaj = 'Merhaba Dünya'",
    2: "yil = 2025",
    3: "pi_sayisi = 3.14",
    4: "hazir_mi = True",
    5: "toplam = 10 + 25",
    6: "kalan = 10 % 3",
    7: "kup = 5 ** 3",
    8: "sonuc = (5 + 2) * 3",
    9: "ad = 'Python'\nsoyad = 'Kursu'\ntam_isim = ad + ' ' + soyad",
    10: "yas = 25\nkisi_bilgisi = f'Yaşım: {yas}'",
    11: "sehir = 'istanbul'\nsehir_buyuk = sehir.upper()",
    12: "alfabe = 'ABCDEF'\nilk_uc = alfabe[:3]",
    13: "metin = 'elma'\nters_metin = metin[::-1]",
    14: "sayilar = [10, 20, 30]",
    15: "renkler = []\nrenkler.append('Mavi')\nrenkler.append('Yesil')",
    16: "meyveler = ['Elma', 'Armut', 'Muz']\nortadaki = meyveler[1]",
    17: "liste = [1, 2, 3, 4, 99]\nliste.pop()",
    18: "kimlik = {'ad': 'Ali', 'yas': 30}",
    19: "kimlik = {'ad': 'Ali', 'yas': 30}\nisim_degeri = kimlik['ad']",
    20: "kimlik = {'ad': 'Ali', 'yas': 30}\nkimlik['meslek'] = 'Mühendis'",
    21: "puan = 85\nif puan > 50:\n    durum = 'Geçti'",
    22: "sayi = 7\nif sayi % 2 == 0:\n    sonuc = 'Çift'\nelse:\n    sonuc = 'Tek'",
    23: "notu = 75\nif notu >= 85:\n    derece = 'A'\nelif notu >= 70:\n    derece = 'B'\nelse:\n    derece = 'C'",
    24: "toplam = 0\nfor i in range(1, 6):\n    toplam += i",
    25: "sayac = 5\nwhile sayac > 0:\n    sayac -= 1",
    26: "sayilar = [10, 20, 30]\nfor x in sayilar:\n    print(x * 2)",
    27: "def kare_al(x):\n    return x * x",
    28: "def carp(a, b):\n    return a * b",
    29: "def selamla(isim='Misafir'):\n    return f'Merhaba {isim}'",
    30: "ikiye_bol = lambda x: x / 2",
    31: "import math\nkarekok = math.sqrt(16)",
    32: "import random\nsansli_sayi = random.randint(1, 100)",
    33: "try:\n    x = 10 / 0\nexcept ZeroDivisionError:\n    sonuc = 'Hata'",
    34: "class Araba:\n    pass",
    35: "class Kedi:\n    def __init__(self, isim):\n        self.isim = isim",
    36: "class Kopek:\n    def havla(self):\n        return 'Hav!'\n\nk = Kopek()\nses = k.havla()",
    37: "kareler = [x**2 for x in range(1, 11)]",
}


# =============================================================================
# GÜVENLİK TEST VAKALARI
# =============================================================================

SECURITY_TEST_CASES = [
    # Dosya erişimi
    ("open('/etc/passwd', 'r').read()", "open", "⛔"),
    ("open('test.txt', 'w').write('hack')", "open", "⛔"),
    
    # Dinamik kod çalıştırma
    ("eval('1+1')", "eval", "⛔"),
    ("exec('x=1')", "exec", "⛔"),
    ("compile('x=1', '', 'exec')", "compile", "⛔"),
    
    # Tehlikeli modül import
    ("import os", "os", "⛔"),
    ("import subprocess", "subprocess", "⛔"),
    ("import socket", "socket", "⛔"),
    ("import sys", "sys", "⛔"),
    ("import shutil", "shutil", "⛔"),
    ("from os import system", "os", "⛔"),
    ("__import__('os')", "os", "⛔"),
    
    # Kapsam erişimi
    ("globals()", "globals", "⛔"),
    ("locals()", "locals", "⛔"),
    
    # Nitelik manipülasyonu
    ("getattr(object, '__class__')", "getattr", "⛔"),
    ("setattr(object, 'x', 1)", "setattr", "⛔"),
    
    # Kullanıcı girişi
    ("input('Adın: ')", "input", "⛔"),
    
    # Hata ayıklayıcı
    ("breakpoint()", "breakpoint", "⛔"),
    
    # Çıkış komutları
    ("exit()", "exit", "⛔"),
    ("quit()", "quit", "⛔"),
]


def test_curriculum_tasks():
    """Tüm 37 müfredat görevini test eder."""
    print("=" * 60)
    print("MÜFREDAT GÖREVLERİ TESTİ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for task_id, code in CURRICULUM_TEST_CASES.items():
        result = run_safe(code, task_id, timeout=5.0)
        
        if result["is_valid"]:
            print(f"✅ Görev {task_id:2d}: BAŞARILI")
            passed += 1
        else:
            print(f"❌ Görev {task_id:2d}: BAŞARISIZ")
            print(f"   Hata: {result['error_message']}")
            failed += 1
    
    print("-" * 60)
    print(f"Sonuç: {passed} başarılı, {failed} başarısız")
    print()
    
    return failed == 0


def test_security_blocks():
    """Güvenlik engellerini test eder."""
    print("=" * 60)
    print("GÜVENLİK ENGELLERİ TESTİ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for code, expected_keyword, expected_emoji in SECURITY_TEST_CASES:
        result = run_safe(code, 1, timeout=2.0)  # task_id önemli değil
        
        error_msg = result.get("error_message", "")
        
        # Güvenlik hatası bekliyoruz
        if expected_emoji in error_msg or "SandboxSecurityError" in str(result):
            print(f"✅ '{code[:40]:<40}': ENGELLENDİ")
            passed += 1
        elif not result["success"]:
            # Başka bir hata olabilir ama yine de engellenmiş
            print(f"✅ '{code[:40]:<40}': ENGELLENDİ (farklı hata)")
            passed += 1
        else:
            print(f"❌ '{code[:40]:<40}': ENGELLENMEDİ!")
            print(f"   Sonuç: {result}")
            failed += 1
    
    print("-" * 60)
    print(f"Sonuç: {passed} engellendi, {failed} engellenmedi")
    print()
    
    return failed == 0


def test_allowed_modules():
    """İzin verilen modülleri test eder."""
    print("=" * 60)
    print("İZİN VERİLEN MODÜLLER TESTİ")
    print("=" * 60)
    
    allowed_tests = [
        ("import math\nx = math.sqrt(16)", "math"),
        ("import random\nx = random.randint(1, 10)", "random"),
        ("import datetime\nx = datetime.datetime.now()", "datetime"),
        ("import string\nx = string.ascii_lowercase", "string"),
        ("import collections\nx = collections.Counter([1,2,3])", "collections"),
        ("import itertools\nx = list(itertools.chain([1], [2]))", "itertools"),
        ("import functools\nx = functools.reduce(lambda a,b: a+b, [1,2,3])", "functools"),
        ("import decimal\nx = decimal.Decimal('1.5')", "decimal"),
        ("import fractions\nx = fractions.Fraction(1, 3)", "fractions"),
    ]
    
    passed = 0
    failed = 0
    
    for code, module_name in allowed_tests:
        result = run_safe(code, 1, timeout=2.0)
        
        if result["success"]:
            print(f"✅ '{module_name}': İZİN VERİLDİ")
            passed += 1
        else:
            print(f"❌ '{module_name}': HATA!")
            print(f"   {result['error_message']}")
            failed += 1
    
    print("-" * 60)
    print(f"Sonuç: {passed} başarılı, {failed} başarısız")
    print()
    
    return failed == 0


if __name__ == "__main__":
    print("\n" + "🔒 SANDBOX DOĞRULAMA TESTLERİ".center(60) + "\n")
    
    curriculum_ok = test_curriculum_tasks()
    security_ok = test_security_blocks()
    modules_ok = test_allowed_modules()
    
    print("=" * 60)
    print("GENEL SONUÇ")
    print("=" * 60)
    
    all_passed = curriculum_ok and security_ok and modules_ok
    
    if all_passed:
        print("✅ TÜM TESTLER BAŞARILI!")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ:")
        if not curriculum_ok:
            print("   - Müfredat görevleri testleri başarısız")
        if not security_ok:
            print("   - Güvenlik engelleri testleri başarısız")
        if not modules_ok:
            print("   - İzin verilen modüller testleri başarısız")
    
    print()
    sys.exit(0 if all_passed else 1)
