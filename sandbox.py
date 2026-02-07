"""
Sandbox Module - Python Kurs Simülatörü için Güvenlik Katmanı

Bu modül, kullanıcı kodunun çalıştırıldığı izole ortamda:
- Yerleşik Python fonksiyonlarına erişimi kısıtlar
- Tehlikeli sistem çağrılarını engeller
- Modül içe aktarmalarını denetler
"""

import builtins

# Orijinal __import__ fonksiyonunu sakla
_original_import = builtins.__import__


class SandboxSecurityError(Exception):
    """Sandbox güvenlik ihlali hatası."""
    pass


# =============================================================================
# İZİN VERİLEN MODÜLLER
# =============================================================================

ALLOWED_MODULES = frozenset([
    # Müfredatta kullanılan modüller
    'math',
    'random', 
    'datetime',
    'json',  # JSON ve API bölümü için eklendi
    # Eğitim amaçlı güvenli yardımcı modüller
    'string',
    'collections',
    'itertools',
    'functools',
    'decimal',
    'fractions',
    'operator',
    'statistics',
    'os',
    'sys',
])


# =============================================================================
# ENGELLENEN FONKSİYONLAR VE HATA MESAJLARI
# =============================================================================

BLOCKED_BUILTINS_MESSAGES = {
    # Dosya işlemleri
    'open': "⛔ Güvenlik: 'open()' fonksiyonu devre dışı. Bu simülatörde dosya işlemleri yapılamaz.",
    
    # Dinamik kod çalıştırma
    'eval': "⛔ Güvenlik: 'eval()' fonksiyonu devre dışı. Dinamik kod çalıştırma yasaktır.",
    'exec': "⛔ Güvenlik: 'exec()' fonksiyonu devre dışı. Dinamik kod çalıştırma yasaktır.",
    'compile': "⛔ Güvenlik: 'compile()' fonksiyonu devre dışı. Kod derleme yasaktır.",
    
    # Kullanıcı girişi
    'input': "⛔ Güvenlik: 'input()' fonksiyonu devre dışı. Bu simülatörde klavye girişi alınamaz.",
    
    # Kapsam erişimi (sandbox kaçış riski)
    'globals': "⛔ Güvenlik: 'globals()' fonksiyonu devre dışı. Global kapsama erişim yasaktır.",
    'locals': "⛔ Güvenlik: 'locals()' fonksiyonu devre dışı. Lokal kapsama erişim yasaktır.",
    
    # Nitelik manipülasyonu (sandbox kaçış riski)
    'getattr': "⛔ Güvenlik: 'getattr()' fonksiyonu devre dışı. Dinamik nitelik erişimi yasaktır.",
    'setattr': "⛔ Güvenlik: 'setattr()' fonksiyonu devre dışı. Dinamik nitelik atama yasaktır.",
    'delattr': "⛔ Güvenlik: 'delattr()' fonksiyonu devre dışı. Dinamik nitelik silme yasaktır.",
    
    # Hata ayıklayıcı
    'breakpoint': "⛔ Güvenlik: 'breakpoint()' fonksiyonu devre dışı. Hata ayıklayıcı erişimi yasaktır.",
    
    # Çıkış komutları
    'exit': "⛔ Güvenlik: 'exit()' komutu devre dışı. Lütfen bu komutu kullanmayın.",
    'quit': "⛔ Güvenlik: 'quit()' komutu devre dışı. Lütfen bu komutu kullanmayın.",
    
    # Etkileşimli komutlar
    'help': "⛔ Güvenlik: 'help()' fonksiyonu devre dışı.",
    'license': "⛔ Güvenlik: 'license()' fonksiyonu devre dışı.",
    'copyright': "⛔ Güvenlik: 'copyright()' fonksiyonu devre dışı.",
    'credits': "⛔ Güvenlik: 'credits()' fonksiyonu devre dışı.",
}


def _create_blocked_builtin(name, message):
    """Çağrıldığında SandboxSecurityError fırlatan bir fonksiyon oluşturur."""
    
    def blocked(*args, **kwargs):
        raise SandboxSecurityError(message)
    
    blocked.__name__ = name
    blocked.__doc__ = f"ENGELLENDI: {message}"
    return blocked


def _create_restricted_import():
    """Kısıtlı __import__ fonksiyonu oluşturur."""
    
    def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
        # Göreceli import'ları engelle
        if level > 0:
            raise SandboxSecurityError(
                "⛔ Güvenlik: Göreceli import (relative import) desteklenmiyor."
            )
        
        # Temel modül adını al (örn: 'os.path' -> 'os')
        base_module = name.split('.')[0]
        
        # Modül izin listesinde mi kontrol et
        if base_module not in ALLOWED_MODULES:
            allowed_list = ', '.join(sorted(ALLOWED_MODULES))
            raise SandboxSecurityError(
                f"⛔ Güvenlik: '{name}' modülü erişime kapalı.\n"
                f"   İzin verilen modüller: {allowed_list}"
            )
        
        # İzin verilen modüller için orijinal import'u kullan
        return _original_import(name, globals, locals, fromlist, level)
    
    return restricted_import


# =============================================================================
# GÜVENLİ YERLEŞİK FONKSİYONLAR (WHITELIST)
# =============================================================================

def _build_safe_builtins():
    """Güvenli yerleşik fonksiyonlar sözlüğünü oluşturur."""
    
    safe = {
        # Sabitler
        'True': True,
        'False': False,
        'None': None,
        
        # Tip oluşturucular
        'bool': bool,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'set': set,
        'frozenset': frozenset,
        'tuple': tuple,
        'complex': complex,
        'bytes': bytes,
        'bytearray': bytearray,
        'memoryview': memoryview,
        
        # Temel fonksiyonlar
        'print': print,
        'len': len,
        'range': range,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'sorted': sorted,
        'reversed': reversed,
        'sum': sum,
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        'pow': pow,
        'divmod': divmod,
        
        # Tip kontrol
        'type': type,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'callable': callable,
        'hasattr': hasattr,  # Sadece okuma için güvenli
        'dir': dir,  # Eğitim amaçlı
        'vars': vars,  # Eğitim amaçlı
        
        # İterasyon
        'iter': iter,
        'next': next,
        
        # String/Formatlama
        'repr': repr,
        'ascii': ascii,
        'chr': chr,
        'ord': ord,
        'format': format,
        'bin': bin,
        'hex': hex,
        'oct': oct,
        
        # Dizi işlemleri
        'slice': slice,
        'all': all,
        'any': any,
        'id': id,
        'hash': hash,
        
        # OOP desteği (Görev 34-36 için gerekli)
        'object': object,
        'super': super,
        'property': property,
        'classmethod': classmethod,
        'staticmethod': staticmethod,
        '__build_class__': builtins.__build_class__,  # Sınıf tanımları için gerekli
        
        # İstisnalar (try/except için gerekli - Görev 33)
        'BaseException': BaseException,
        'Exception': Exception,
        'ArithmeticError': ArithmeticError,
        'AssertionError': AssertionError,
        'AttributeError': AttributeError,
        'BlockingIOError': BlockingIOError,
        'BrokenPipeError': BrokenPipeError,
        'BufferError': BufferError,
        'BytesWarning': BytesWarning,
        'ChildProcessError': ChildProcessError,
        'ConnectionAbortedError': ConnectionAbortedError,
        'ConnectionError': ConnectionError,
        'ConnectionRefusedError': ConnectionRefusedError,
        'ConnectionResetError': ConnectionResetError,
        'DeprecationWarning': DeprecationWarning,
        'EOFError': EOFError,
        'EnvironmentError': EnvironmentError,
        'FileExistsError': FileExistsError,
        'FileNotFoundError': FileNotFoundError,
        'FloatingPointError': FloatingPointError,
        'FutureWarning': FutureWarning,
        'GeneratorExit': GeneratorExit,
        'IOError': IOError,
        'ImportError': ImportError,
        'ImportWarning': ImportWarning,
        'IndentationError': IndentationError,
        'IndexError': IndexError,
        'InterruptedError': InterruptedError,
        'IsADirectoryError': IsADirectoryError,
        'KeyError': KeyError,
        'KeyboardInterrupt': KeyboardInterrupt,
        'LookupError': LookupError,
        'MemoryError': MemoryError,
        'ModuleNotFoundError': ModuleNotFoundError,
        'NameError': NameError,
        'NotADirectoryError': NotADirectoryError,
        'NotImplemented': NotImplemented,
        'NotImplementedError': NotImplementedError,
        'OSError': OSError,
        'OverflowError': OverflowError,
        'PendingDeprecationWarning': PendingDeprecationWarning,
        'PermissionError': PermissionError,
        'ProcessLookupError': ProcessLookupError,
        'RecursionError': RecursionError,
        'ReferenceError': ReferenceError,
        'ResourceWarning': ResourceWarning,
        'RuntimeError': RuntimeError,
        'RuntimeWarning': RuntimeWarning,
        'StopAsyncIteration': StopAsyncIteration,
        'StopIteration': StopIteration,
        'SyntaxError': SyntaxError,
        'SyntaxWarning': SyntaxWarning,
        'SystemError': SystemError,
        'SystemExit': SystemExit,
        'TabError': TabError,
        'TimeoutError': TimeoutError,
        'TypeError': TypeError,
        'UnboundLocalError': UnboundLocalError,
        'UnicodeDecodeError': UnicodeDecodeError,
        'UnicodeEncodeError': UnicodeEncodeError,
        'UnicodeError': UnicodeError,
        'UnicodeTranslateError': UnicodeTranslateError,
        'UnicodeWarning': UnicodeWarning,
        'UserWarning': UserWarning,
        'ValueError': ValueError,
        'Warning': Warning,
        'ZeroDivisionError': ZeroDivisionError,
        
        # Ellipsis (gelişmiş dilimleme için)
        'Ellipsis': Ellipsis,
        
        # Kısıtlı import fonksiyonu
        '__import__': _create_restricted_import(),
        
        # Sandbox güvenlik hatası (kullanıcının yakalaması için)
        'SandboxSecurityError': SandboxSecurityError,
    }
    
    # Engellenen fonksiyonları ekle
    for name, message in BLOCKED_BUILTINS_MESSAGES.items():
        safe[name] = _create_blocked_builtin(name, message)
    
    return safe


# Güvenli yerleşikler sözlüğünü önbelleğe al
_SAFE_BUILTINS = None

def get_safe_builtins():
    """Önbelleğe alınmış güvenli yerleşikler sözlüğünü döndürür."""
    global _SAFE_BUILTINS
    if _SAFE_BUILTINS is None:
        _SAFE_BUILTINS = _build_safe_builtins()
    return _SAFE_BUILTINS


def get_sandbox_scope(fs=None):
    """
    Kullanıcı kodu için güvenli çalıştırma kapsamını döndürür.
    
    Args:
        fs: (Opsiyonel) MockFileSystem örneği.
            Verilirse 'open' fonksiyonu bu dosya sistemini kullanır.
    
    Returns:
        dict: Güvenli çalıştırma kapsamı
    """
    import math
    import random
    import datetime
    
    scope = {
        # Önceden yüklenmiş güvenli modüller (müfredat için gerekli)
        'math': math,
        'random': random,
        'datetime': datetime,
        
        # Standart __name__ değeri
        '__name__': '__main__',
        
        # Kısıtlı yerleşikler
        '__builtins__': get_safe_builtins(),
    }
    
    # Eğer dosya sistemi verildiyse, güvenli open fonksiyonunu ekle
    if fs:
        scope['open'] = fs.open
    
    return scope
