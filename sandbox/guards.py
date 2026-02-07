"""
Resource Guard Module - Python Kurs Simülatörü için Kaynak Koruma Katmanı

Bu modül, kullanıcı kodunun çalıştırıldığı izole ortamda:
- Bellek kullanımını sınırlar
- CPU zaman tüketimini kontrol eder
- Sonsuz döngüleri tespit edip sonlandırır
- Özyineleme derinliğini kontrol eder
"""

import sys
import platform
import tracemalloc
from contextlib import contextmanager
from typing import Optional

# Platform kontrolü
IS_UNIX = platform.system() in ('Linux', 'Darwin')  # Linux veya macOS

# Unix-specific imports
if IS_UNIX:
    try:
        import resource
        import signal
        HAS_RESOURCE = True
    except ImportError:
        HAS_RESOURCE = False
else:
    HAS_RESOURCE = False


# =============================================================================
# KAYNAK LİMİT HATASI
# =============================================================================

class ResourceLimitError(Exception):
    """Kaynak limiti aşıldığında fırlatılan hata."""
    pass


class MemoryLimitError(ResourceLimitError):
    """Bellek limiti aşıldığında fırlatılan hata."""
    pass


class CPULimitError(ResourceLimitError):
    """CPU zaman limiti aşıldığında fırlatılan hata."""
    pass


class OperationLimitError(ResourceLimitError):
    """İşlem (döngü) limiti aşıldığında fırlatılan hata."""
    pass


class RecursionLimitError(ResourceLimitError):
    """Özyineleme limiti aşıldığında fırlatılan hata."""
    pass


# =============================================================================
# TÜRKÇE HATA MESAJLARI
# =============================================================================

ERROR_MESSAGES = {
    'memory': "💾 Bellek limiti aşıldı. Çok büyük veri yapıları oluşturmayın.",
    'cpu': "⚡ İşlemci zaman limiti aşıldı. Kodunuz çok yoğun hesaplamalar yapıyor.",
    'loop': "⏰ Kodunuz çok fazla işlem yaptı. Sonsuz döngü olabilir mi?",
    'recursion': "🔄 Fonksiyon kendini çok fazla çağırdı (özyineleme limiti aşıldı).",
}


# =============================================================================
# LOOP GUARD - SYS.SETTRACE İLE İŞLEM SAYACI
# =============================================================================

class LoopGuard:
    """
    sys.settrace kullanarak çalıştırılan işlem sayısını takip eder.
    Belirli bir limiti aşınca OperationLimitError fırlatır.
    
    Not: sys.settrace her satırda çağrıldığı için performans etkisi vardır.
    Bu nedenle sadece sandbox içinde kullanılmalıdır.
    """
    
    def __init__(self, max_operations: int = 1_000_000):
        self.max_operations = max_operations
        self.operation_count = 0
        self._previous_trace = None
    
    def _trace_calls(self, frame, event, arg):
        """Her satır çalıştığında çağrılır."""
        if event == 'line':
            self.operation_count += 1
            if self.operation_count > self.max_operations:
                raise OperationLimitError(ERROR_MESSAGES['loop'])
        return self._trace_calls
    
    def enable(self):
        """İşlem sayacını aktifleştirir."""
        self.operation_count = 0
        self._previous_trace = sys.gettrace()
        sys.settrace(self._trace_calls)
    
    def disable(self):
        """İşlem sayacını devre dışı bırakır."""
        sys.settrace(self._previous_trace)
        self._previous_trace = None


# =============================================================================
# MEMORY GUARD - TRACEMALLOC İLE BELLEK TAKİBİ
# =============================================================================

class MemoryGuard:
    """
    tracemalloc kullanarak bellek kullanımını takip eder.
    Unix sistemlerde resource.setrlimit ile hard limit koyar.
    """
    
    def __init__(self, memory_limit_mb: int = 50):
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self._original_limit = None
    
    def enable(self):
        """Bellek takibini başlatır ve limitleri uygular."""
        # tracemalloc başlat (cross-platform)
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        # Unix'te hard limit koy
        if HAS_RESOURCE:
            try:
                # Mevcut limiti sakla
                self._original_limit = resource.getrlimit(resource.RLIMIT_AS)
                # Yeni limit uygula
                resource.setrlimit(
                    resource.RLIMIT_AS, 
                    (self.memory_limit_bytes, self.memory_limit_bytes)
                )
            except (ValueError, resource.error):
                # Limit uygulanamadıysa devam et (bazı sistemlerde izin olmayabilir)
                self._original_limit = None
    
    def disable(self):
        """Bellek takibini durdurur ve limitleri geri alır."""
        # tracemalloc'u durdur
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        
        # Unix'te orijinal limiti geri yükle
        if HAS_RESOURCE and self._original_limit is not None:
            try:
                resource.setrlimit(resource.RLIMIT_AS, self._original_limit)
            except (ValueError, resource.error):
                pass
            self._original_limit = None
    
    def check_memory(self):
        """Mevcut bellek kullanımını kontrol eder."""
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            if current > self.memory_limit_bytes:
                raise MemoryLimitError(ERROR_MESSAGES['memory'])


# =============================================================================
# CPU GUARD - SIGNAL.ALARM İLE CPU ZAMANI (UNIX ONLY)
# =============================================================================

class CPUGuard:
    """
    Unix sistemlerde signal.SIGALRM kullanarak CPU zamanını sınırlar.
    Windows'ta bu guard pasif kalır (timeout multiprocessing ile sağlanır).
    """
    
    def __init__(self, cpu_time_limit_s: int = 5):
        self.cpu_time_limit = cpu_time_limit_s
        self._original_handler = None
    
    def _alarm_handler(self, signum, frame):
        """SIGALRM sinyali alındığında çağrılır."""
        raise CPULimitError(ERROR_MESSAGES['cpu'])
    
    def enable(self):
        """CPU zamanı limitini uygular."""
        if HAS_RESOURCE:
            try:
                # Mevcut handler'ı sakla
                self._original_handler = signal.signal(signal.SIGALRM, self._alarm_handler)
                # CPU limiti ayarla
                resource.setrlimit(
                    resource.RLIMIT_CPU,
                    (self.cpu_time_limit, self.cpu_time_limit)
                )
                # Alarm kur (backup olarak)
                signal.alarm(self.cpu_time_limit)
            except (ValueError, resource.error, AttributeError):
                self._original_handler = None
    
    def disable(self):
        """CPU zamanı limitini kaldırır."""
        if HAS_RESOURCE and self._original_handler is not None:
            try:
                # Alarm'ı iptal et
                signal.alarm(0)
                # Orijinal handler'ı geri yükle
                signal.signal(signal.SIGALRM, self._original_handler)
            except (ValueError, AttributeError):
                pass
            self._original_handler = None


# =============================================================================
# RECURSION GUARD - SYS.SETRECURSIONLIMIT
# =============================================================================

class RecursionGuard:
    """
    sys.setrecursionlimit kullanarak özyineleme derinliğini sınırlar.
    Cross-platform çalışır.
    """
    
    def __init__(self, recursion_limit: int = 500):
        self.recursion_limit = recursion_limit
        self._original_limit = None
    
    def enable(self):
        """Özyineleme limitini uygular."""
        self._original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.recursion_limit)
    
    def disable(self):
        """Özyineleme limitini geri alır."""
        if self._original_limit is not None:
            sys.setrecursionlimit(self._original_limit)
            self._original_limit = None


# =============================================================================
# RESOURCE GUARDIAN - MERKEZİ CONTEXT MANAGER
# =============================================================================

class ResourceGuardian:
    """
    Tüm kaynak koruma mekanizmalarını yöneten merkezi context manager.
    
    Kullanım:
        with ResourceGuardian() as guard:
            exec(user_code, scope)
    
    Parameters:
        memory_limit_mb: Maksimum bellek kullanımı (MB)
        cpu_time_limit_s: Maksimum CPU zamanı (saniye)
        max_operations: Maksimum işlem sayısı (döngü kontrolü)
        recursion_limit: Maksimum özyineleme derinliği
        enable_loop_guard: LoopGuard'ı aktif et (performans etkisi var)
    """
    
    def __init__(
        self,
        memory_limit_mb: int = 100,  # Eğitim amaçlı geniş tutuldu
        cpu_time_limit_s: int = 5,
        max_operations: int = 2_000_000,  # 2M işlem - geniş tutuldu
        recursion_limit: int = 500,
        enable_loop_guard: bool = True
    ):
        self.memory_guard = MemoryGuard(memory_limit_mb)
        self.cpu_guard = CPUGuard(cpu_time_limit_s)
        self.loop_guard = LoopGuard(max_operations) if enable_loop_guard else None
        self.recursion_guard = RecursionGuard(recursion_limit)
    
    def __enter__(self):
        """Tüm guard'ları aktifleştirir."""
        # Sıralama önemli: önce basit, sonra karmaşık
        self.recursion_guard.enable()
        self.memory_guard.enable()
        self.cpu_guard.enable()
        if self.loop_guard:
            self.loop_guard.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Tüm guard'ları devre dışı bırakır."""
        # Ters sırada kapat
        if self.loop_guard:
            self.loop_guard.disable()
        self.cpu_guard.disable()
        self.memory_guard.disable()
        self.recursion_guard.disable()
        
        # RecursionError'u daha anlaşılır mesajla değiştir
        if exc_type is RecursionError:
            raise RecursionLimitError(ERROR_MESSAGES['recursion']) from None
        
        # MemoryError'u daha anlaşılır mesajla değiştir
        if exc_type is MemoryError:
            raise MemoryLimitError(ERROR_MESSAGES['memory']) from None
        
        # Diğer hataları olduğu gibi bırak
        return False


# =============================================================================
# HELPER FONKSİYONLAR
# =============================================================================

@contextmanager
def guarded_execution(
    memory_limit_mb: int = 100,
    cpu_time_limit_s: int = 5,
    max_operations: int = 2_000_000,
    recursion_limit: int = 500
):
    """
    ResourceGuardian için kolaylık fonksiyonu.
    
    Kullanım:
        with guarded_execution() as guard:
            exec(code, scope)
    """
    guardian = ResourceGuardian(
        memory_limit_mb=memory_limit_mb,
        cpu_time_limit_s=cpu_time_limit_s,
        max_operations=max_operations,
        recursion_limit=recursion_limit
    )
    with guardian as g:
        yield g
