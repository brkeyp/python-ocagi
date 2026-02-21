import multiprocessing
import sys
import io
import contextlib

def _worker_process(user_code, validator_script_path, result_queue):
    """
    Bu fonksiyon ayrı bir işlemde (process) çalışır.
    """
    # 1. Güvenli Scope Hazırla (sandbox modülü ile)
    from sandbox.security import get_sandbox_scope
    from sandbox.guards import ResourceGuardian, ResourceLimitError
    from sandbox.vfs import MockFileSystem
    import importlib.util
    import os
    
    fs = MockFileSystem()
    scope = get_sandbox_scope(fs=fs)
    
    import io
    output_capture = io.StringIO()
    success = False
    error_message = ""
    is_valid = False
    stdout_val = ""

    try:
        # 2. Kodu Çalıştır
        with ResourceGuardian(
            memory_limit_mb=100,
            cpu_time_limit_s=5,
            max_operations=2_000_000,
            recursion_limit=500
        ):
            import contextlib
            with contextlib.redirect_stdout(output_capture):
                exec(user_code, scope)
        
        success = True
        stdout_val = output_capture.getvalue()

    except Exception as e:
        # Hata yakalama (kısaltılmış for brevity temp)
        error_message = f"Hata: {str(e)}"
        # Catch specific types if needed as before
        if isinstance(e, SyntaxError):
             error_message = f"Yazım Hatası: {e.msg} Line {e.lineno}"
        elif isinstance(e, ResourceLimitError):
             error_message = str(e)

    # 3. Doğrulama
    if success:
        if validator_script_path and os.path.exists(validator_script_path):
            try:
                # Load Validator Module Dynamically
                spec = importlib.util.spec_from_file_location("validation_mod", validator_script_path)
                val_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(val_module)
                
                if hasattr(val_module, 'validate'):
                    # Validator scope üzerinde çalışır
                    if val_module.validate(scope, stdout_val):
                        is_valid = True
                    else:
                        error_message = "Kod çalıştı ama sonuç beklendiği gibi değil."
                else:
                    error_message = "Doğrulama dosyası hatalı (validate fonksiyonu yok)."
            except Exception as e:
                success = False
                error_message = f"Kontrol sırasında hata oluştu: {e}"
        else:
            # Validator yoksa hata ver
            is_valid = False
            error_message = "SİSTEM HATASI: Doğrulama (validation.py) dosyası bulunamadı."

    # Sonucu kuyruğa at
    result_queue.put({
        "success": success,
        "stdout": stdout_val,
        "is_valid": is_valid,
        "error_message": error_message
    })


def run_safe(user_code, validator_script_path, timeout=None):
    """
    Args:
        user_code: Kod stringi
        validator_script_path: Validator dosyasının tam yolu (str)
    """
    import config
    if timeout is None:
        timeout = config.Timing.EXECUTION_TIMEOUT
    import multiprocessing
    queue = multiprocessing.Queue()
    
    process = multiprocessing.Process(
        target=_worker_process,
        args=(user_code, validator_script_path, queue)
    )
    process.start()
    process.join(timeout)
    
    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "success": False,
            "stdout": "",
            "is_valid": False,
            "error_message": f"⏳ Zaman Aşımı ({timeout}s)"
        }
    
    if not queue.empty():
        return queue.get()
    else:
        return {
            "success": False,
            "stdout": "",
            "is_valid": False,
            "error_message": "⚠️ Kritik İşlem Hatası"
        }
