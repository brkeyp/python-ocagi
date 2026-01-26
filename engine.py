import json
import os
import sys
import io
import contextlib
import time
import validators
import curses
from ui import run_editor_session
from ui_utils import OSUtils

@contextlib.contextmanager
def suspend_curses(stdscr):
    """Curses modunu geçici olarak askıya alır (print/input için)."""
    curses.endwin()
    yield
    stdscr.refresh()

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CURRICULUM_FILE = os.path.join(DATA_DIR, 'curriculum.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'progress.json')

def load_curriculum():
    with open(CURRICULUM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

PROGRESS_BACKUP_FILE = os.path.join(DATA_DIR, 'progress.backup.json')

def get_default_progress():
    """Varsayılan ilerleme yapısını döndürür."""
    return {
        "current_step_id": 1,
        "highest_reached_id": 1,
        "user_codes": {},
        "completed_tasks": [],
        "skipped_tasks": []
    }

def validate_progress_data(data):
    """İlerleme verisinin geçerliliğini kontrol eder ve düzeltir."""
    default = get_default_progress()
    
    if not isinstance(data, dict):
        return default
    
    # Eksik alanları varsayılanlarla doldur
    for key, value in default.items():
        if key not in data:
            data[key] = value
    
    # Tip kontrolü ve düzeltme
    if not isinstance(data.get("current_step_id"), int) or data["current_step_id"] < 1:
        data["current_step_id"] = 1
    
    if not isinstance(data.get("highest_reached_id"), int) or data["highest_reached_id"] < 1:
        data["highest_reached_id"] = data["current_step_id"]
    
    # highest_reached_id en az current_step_id kadar olmalı
    if data["highest_reached_id"] < data["current_step_id"]:
        data["highest_reached_id"] = data["current_step_id"]
    
    if not isinstance(data.get("user_codes"), dict):
        data["user_codes"] = {}
    
    if not isinstance(data.get("completed_tasks"), list):
        data["completed_tasks"] = []
    
    if not isinstance(data.get("skipped_tasks"), list):
        data["skipped_tasks"] = []
    
    return data

def load_progress():
    """İlerleme dosyasını yükler, eksik alanları varsayılanlarla doldurur."""
    default = get_default_progress()
    
    # Ana dosyayı dene
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return validate_progress_data(data)
        except (json.JSONDecodeError, IOError, OSError):
            # Ana dosya bozuksa yedekten dene
            pass
    
    # Yedek dosyayı dene
    if os.path.exists(PROGRESS_BACKUP_FILE):
        try:
            with open(PROGRESS_BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            validated = validate_progress_data(data)
            # Yedekten yüklendiyse ana dosyayı güncelle
            save_progress_data(validated)
            return validated
        except (json.JSONDecodeError, IOError, OSError):
            pass
    
    # Her iki dosya da yoksa veya bozuksa varsayılan döndür
    return default

def save_progress_data(progress_data):
    """Tam ilerleme verisini kaydeder (yedekle birlikte)."""
    # Önce mevcut dosyayı yedekle (varsa)
    if os.path.exists(PROGRESS_FILE):
        try:
            import shutil
            shutil.copy2(PROGRESS_FILE, PROGRESS_BACKUP_FILE)
        except (IOError, OSError):
            pass  # Yedekleme başarısız olursa devam et
    
    # Yeni veriyi kaydet (Atomic Write-Replace Pattern)
    temp_file = PROGRESS_FILE + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        # Atomik değiştirme
        os.replace(temp_file, PROGRESS_FILE)
        
    except (IOError, OSError) as e:
        # Kaydetme başarısız olursa varsa temp dosyasını temizle
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass
                
        # Kullanıcıya bildir (ama çökme)
        print(f"\n⚠️  İlerleme kaydedilemedi: {e}")

def save_progress(current_step_id):
    """Geriye uyumluluk için: sadece current_step_id güncelleyerek kaydeder."""
    progress = load_progress()
    progress["current_step_id"] = current_step_id
    
    # highest_reached_id'yi güncelle (eğer daha ileriye gidildiyse)
    if current_step_id > progress.get("highest_reached_id", 1):
        progress["highest_reached_id"] = current_step_id
    
    save_progress_data(progress)

def save_user_code(step_id, code):
    """Kullanıcının yazdığı kodu kaydeder."""
    progress = load_progress()
    progress["user_codes"][str(step_id)] = code
    save_progress_data(progress)

def get_user_code(step_id):
    """Kullanıcının daha önce yazdığı kodu döndürür."""
    progress = load_progress()
    return progress.get("user_codes", {}).get(str(step_id), "")

def mark_task_completed(step_id):
    """Görevi tamamlandı olarak işaretler."""
    progress = load_progress()
    if step_id not in progress["completed_tasks"]:
        progress["completed_tasks"].append(step_id)
    # Atlanmış listesinden çıkar (eğer önceden atlanmışsa)
    if step_id in progress["skipped_tasks"]:
        progress["skipped_tasks"].remove(step_id)
    save_progress_data(progress)

def mark_task_skipped(step_id):
    """Görevi atlandı olarak işaretler."""
    progress = load_progress()
    if step_id not in progress["skipped_tasks"]:
        progress["skipped_tasks"].append(step_id)
    save_progress_data(progress)

def reset_all_progress():
    """Tüm ilerlemeyi sıfırlar."""
    save_progress_data(get_default_progress())

def reset_scope():
    """Temel kullanım için scope hazırlar."""
    import math
    import random
    import datetime
    return {
        'math': math,
        'random': random,
        'datetime': datetime
    }

def _run_simulation_loop(stdscr):
    curriculum = load_curriculum()
    # Scope artık safe_runner içinde yönetiliyor, burada tutmaya gerek yok.
    # user_scope = reset_scope()  <-- KALDIRILDI
    
    # Curses ayarları - Ana döngü tek bir init ile çalışacak
    curses.curs_set(1)
    
    while True:
        progress = load_progress()
        current_step_id = progress.get("current_step_id", 1)
        
        # Görev durumu tespiti
        is_completed = current_step_id in progress.get("completed_tasks", [])
        is_skipped = current_step_id in progress.get("skipped_tasks", [])
        task_status = "completed" if is_completed else ("skipped" if is_skipped else "pending")
        
        # Sayaç bilgileri
        completed_count = len(progress.get("completed_tasks", []))
        skipped_count = len(progress.get("skipped_tasks", []))
        
        # Mevcut adımı bul
        step = next((item for item in curriculum if item["id"] == current_step_id), None)
        
        if not step:
            # Atlanmış görev var mı kontrol et
            skipped_tasks = progress.get("skipped_tasks", [])
            has_skipped = len(skipped_tasks) > 0
            
            # Tebrikler ekranını curses UI ile göster
            result = run_editor_session(
                stdscr,
                task_info="",  # Boş - özel celebration modu
                hint_text="",
                initial_code="",
                task_status="celebration",  # Yeni özel durum
                completed_count=completed_count,
                skipped_count=skipped_count,
                has_skipped=has_skipped
            )
            
            if result == "GOTO_FIRST_SKIPPED" and skipped_tasks:
                # Atlanmış ilk göreve git
                first_skipped = min(skipped_tasks)
                progress["current_step_id"] = first_skipped
                save_progress_data(progress)
                continue
            elif result == "DEV_MESSAGE":
                # Geliştirici mesajı ekranını göster (Suspend ederek)
                with suspend_curses(stdscr):
                    try:
                        from ui_dev_message import show_developer_message
                        show_developer_message()
                    except:
                        pass
                continue
            elif result == "PREV_TASK":
                # Son göreve git (highest_reached_id - 1)
                highest = progress.get("highest_reached_id", 1)
                if highest > 1:
                    progress["current_step_id"] = highest - 1
                    save_progress_data(progress)
                continue
            elif result == "NEXT_TASK":
                # Zaten sondayız, celebration ekranına geri dön
                continue
            elif result == "RESET_ALL":
                # Sıfırlama işlemi (Suspend ederek print göster)
                with suspend_curses(stdscr):
                    reset_all_progress()
                    # user_scope = reset_scope() <-- ARTIK YOK
                    OSUtils.clear_screen()
                    print("\n🗑️  İLERLEME SIFIRLANDI!")
                    print("Yolculuğa en baştan başlıyoruz...")
                    time.sleep(2)
                continue
            else:
                # Çıkış (Ctrl+C veya None)
                break
        
        # Durum damgası
        if is_completed:
            status_badge = " - BAŞARILDI"
        elif is_skipped:
            status_badge = " - ATLANDI"
        else:
            status_badge = ""
            
        # Görev metnini hazırla
        task_info = f"BÖLÜM: {step['cat']}\n"
        
        # Task içeriğini analiz et (Başlık ve Açıklama Ayrımı)
        raw_task = step['task']
        if '\n' in raw_task:
            title_line, desc_part = raw_task.split('\n', 1)
            if title_line.strip().startswith(str(step['id']) + "."):
                clean_title = title_line.split('.', 1)[1].strip().strip(':')
                task_info += f"GÖREV {step['id']}: {clean_title}{status_badge}\n"
                task_info += f"\nSORU: {desc_part}"
            else:
                task_info += f"GÖREV {step['id']}: {title_line}{status_badge}\n"
                task_info += f"\nSORU: {desc_part}"
        else:
             task_info += f"GÖREV {step['id']}:{status_badge}\n"
             task_info += f"\nSORU: {raw_task}"
        
        hint_text = step['hint']
        previous_code = get_user_code(current_step_id)
        
        # Editörü Başlat (Session içinde)
        user_code = run_editor_session(
            stdscr,
            task_info=task_info, 
            hint_text=hint_text, 
            initial_code=previous_code,
            task_status=task_status,
            completed_count=completed_count,
            skipped_count=skipped_count
        )
        
        if user_code == "RESET_ALL":
             # SIFIRLAMA İŞLEMİ
             with suspend_curses(stdscr):
                 reset_all_progress()
                 # user_scope = reset_scope() <-- ARTIK YOK
                 OSUtils.clear_screen()
                 print("\n🗑️  İLERLEME SIFIRLANDI!")
                 print("Yolculuğa en baştan başlıyoruz...")
                 time.sleep(2)
             continue
        
        if user_code == "DEV_MESSAGE":
            # Geliştirici mesajı
            with suspend_curses(stdscr):
                from ui_dev_message import show_developer_message
                show_developer_message()
            continue
        
        if user_code == "PREV_TASK":
            # Önceki soruya git
            if current_step_id > 1:
                progress = load_progress()
                progress["current_step_id"] = current_step_id - 1
                save_progress_data(progress)
            continue
        
        if user_code == "NEXT_TASK":
            # Sonraki soruya git
            progress = load_progress()
            highest_reached = progress.get("highest_reached_id", current_step_id)
            if current_step_id < highest_reached:
                progress["current_step_id"] = current_step_id + 1
                save_progress_data(progress)
            continue
        
        if user_code == "SHOW_SOLUTION":
            # Çözümü göster
            with suspend_curses(stdscr):
                OSUtils.clear_screen()
                print("\n📖 ÇÖZÜM")
                print("-" * 30)
                print(f"\n{step['sol']}\n")
                print("-" * 30)
                input("\nDevam etmek için Enter'a bas...")
            continue

        if user_code is None:
            # Soru Atlandı Modu
            with suspend_curses(stdscr):
                OSUtils.clear_screen()
                
                if is_skipped:
                    print("\n📖 ÇÖZÜM (Daha önce atlanmış görev)")
                else:
                    print("\n⏩ SORU ATLANDI")
                    
                print("-" * 30)
                print("✅ Bu sorunun DOĞRU ÇÖZÜMÜ:")
                print(f"\n{step['sol']}\n")
                print("-" * 30)
                
                if not is_skipped:
                    mark_task_skipped(current_step_id)
                    save_progress(current_step_id + 1)
                
                print("\nDevam etmek için Enter'a bas...")
                input()
            continue

        # --- GÜVENLİ ÇALIŞTIRMA MODU (SAFE RUNNER) ---
        from safe_runner import run_safe
        
        # safe_runner hem çalıştırmayı hem de validasyonu halleder
        result = run_safe(user_code, step['id'])
        
        success = result["success"]
        stdout_val = result["stdout"]
        is_valid = result["is_valid"]
        error_message = result["error_message"]
        
        # Kullanıcının yazdığı kodu kaydet
        save_user_code(current_step_id, user_code)
        
        # Sonuç Ekranı (Suspend ederek)
        with suspend_curses(stdscr):
            OSUtils.clear_screen()
            if is_valid:
                print("\n✅ TEBRİKLER! DOĞRU CEVAP.")
                if stdout_val:
                    print(f"\nKod Çıktısı:\n{stdout_val}")
                
                if is_skipped:
                    print("\n📝 Not: Bu görev daha önce atlandığı için 'Atlandı' olarak kayıtlı kalacak.")
                    input("\nDevam etmek için Enter'a bas...")
                else:
                    mark_task_completed(current_step_id)
                    save_progress(current_step_id + 1)
                    time.sleep(1.5)
            else:
                print("\n❌ HATA VEYA YANLIŞ CEVAP")
                print("-" * 30)
                print(f"Hata Detayı: {error_message}")
                if stdout_val:
                    print(f"Kod Çıktısı: {stdout_val}")
                print("-" * 30)
                print("\nTekrar denemek için Enter'a bas...")
                input()

def run_simulation():
    # macOS üzerinde spawn methodu kullanılması önerilir (fork sorun çıkarabilir)
    import multiprocessing
    multiprocessing.set_start_method('spawn', force=True)
    curses.wrapper(_run_simulation_loop)
