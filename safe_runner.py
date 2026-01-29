import multiprocessing
import sys
import io
import contextlib
import validators
import time

def _worker_process(user_code, step_id, result_queue):
    """
    Bu fonksiyon ayrı bir işlemde (process) çalışır.
    Kullanıcı kodunu izole bir ortamda çalıştırır ve sonucu doğrular.
    """
    # 1. Güvenli Scope Hazırla (sandbox modülü ile)
    from sandbox import get_sandbox_scope
    from resource_guard import ResourceGuardian, ResourceLimitError
    
    scope = get_sandbox_scope()
    
    output_capture = io.StringIO()
    success = False
    error_message = ""
    is_valid = False
    stdout_val = ""

    try:
        # 2. Kodu Çalıştır (Kaynak limitleri ile korumalı)
        with ResourceGuardian(
            memory_limit_mb=100,      # 100 MB bellek limiti
            cpu_time_limit_s=5,       # 5 saniye CPU limiti
            max_operations=2_000_000, # 2M işlem (sonsuz döngü koruması)
            recursion_limit=500       # 500 özyineleme derinliği
        ):
            with contextlib.redirect_stdout(output_capture):
                exec(user_code, scope)
        
        success = True
        stdout_val = output_capture.getvalue()

    except SyntaxError as e:
        error_message = f"Yazım Hatası (Syntax Error): {e.msg}\n"
        if e.text:
            error_message += f"Satır {e.lineno}:\n"
            error_message += f"  {e.text.rstrip()}\n"
            if e.offset:
                indent = "  " + " " * (e.offset - 1)
                error_message += f"{indent}^\n"
        else:
            error_message += f"Satır {e.lineno}"
    
    except ResourceLimitError as e:
        # Kaynak limiti hatalarını yakala (Türkçe mesajlar resource_guard'dan gelir)
        error_message = str(e)
    
    except SystemExit:
        error_message = "⚠️  UYARI: Kod 'sys.exit()' veya benzeri bir çıkış komutu içeriyor. Lütfen bunu yapma."
    except KeyboardInterrupt:
        error_message = "⚠️  İşlem kullanıcı tarafından durduruldu."
    except RecursionError:
        error_message = "🔄 Fonksiyon kendini çok fazla çağırdı (özyineleme limiti aşıldı)."
    except MemoryError:
        error_message = "💾 Bellek limiti aşıldı. Çok büyük veri yapıları oluşturmayın."
    except Exception as e:
        # Traceback detaylarını burada kısaltabiliriz ama şimdilik str(e) yeterli
        error_message = f"Çalışma Zamanı Hatası (Runtime Error): {str(e)}"
    except:
         error_message = "Bilinmeyen kritik bir hata oluştu."

    # 3. Doğrulama (Sadece kod başarıyla çalıştıysa)
    if success:
        validator_func = validators.get_validator(step_id)
        if validator_func:
            try:
                # Validator scope üzerinde çalışır
                if validator_func(scope, stdout_val):
                    is_valid = True
                else:
                    error_message = "Kod çalıştı ama sonuç beklendiği gibi değil."
            except Exception as e:
                success = False # Validasyon patlarsa başarıyı geri al
                error_message = f"Kontrol sırasında hata oluştu: {e}"
        else:
            # Validator yoksa (örneğin sadece çalıştırma görevi)
            # Şu anki mantıkta validator yoksa hata dönüyor gibi engine.py'de
            # ama burada task'a göre değişebilir. engine.py'ye sadık kalalım:
            error_message = "Bu görev için doğrulama fonksiyonu bulunamadı."
            success = False

    # Sonucu kuyruğa at
    result_queue.put({
        "success": success,
        "stdout": stdout_val,
        "is_valid": is_valid,
        "error_message": error_message
    })


def run_safe(user_code, step_id, timeout=2.0):
    """
    Kullanıcı kodunu güvenli bir şekilde çalıştırır.
    Zaman aşımı (timeout) kontrolü yapar.
    """
    # Multiprocessing Queue - sonuçları almak için
    queue = multiprocessing.Queue()
    
    # İşlemi Başlat
    process = multiprocessing.Process(
        target=_worker_process,
        args=(user_code, step_id, queue)
    )
    process.start()
    
    # Zaman aşımı beklemesi
    process.join(timeout)
    
    if process.is_alive():
        # Süre doldu, işlemi öldür
        process.terminate()
        process.join()
        return {
            "success": False,
            "stdout": "",
            "is_valid": False,
            "error_message": f"⏳ Zaman Aşımı: Kodunuz {timeout} saniye içinde tamamlanmadı. Sonsuz döngü olabilir mi?"
        }
    
    # Kuyruktan sonucu al
    if not queue.empty():
        return queue.get()
    else:
        # Kuyruk boşsa ve process bittiyse, muhtemelen crash olmuştur (C seviyesi vs)
        return {
            "success": False,
            "stdout": "",
            "is_valid": False,
            "error_message": "⚠️  Kritik Hata: İşlem beklenmedik şekilde sonlandı (Memory Error veya Segmentation Fault olabilir)."
        }
