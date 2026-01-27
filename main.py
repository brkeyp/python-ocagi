# -*- coding: utf-8 -*-
import sys
import os

import os
import config

# Curses escape delay fix (Must be set before any curses import/init)
os.environ.setdefault('ESCDELAY', config.Timing.ESCDELAY_ENV)

import subprocess


def get_script_path():
    """Çalışan script'in tam yolunu döndürür."""
    return os.path.abspath(__file__)


def install_python_313_silent():
    """Python 3.13'ü sessiz/katılımsız yükler."""
    import urllib.request
    import tempfile
    import hashlib
    
    # SHA-256 Checksum for Python 3.13.11 amd64
    # Güncelleme durumunda bu hash'in de güncellenmesi GEREKLİDİR.
    EXPECTED_HASH = config.System.PYTHON_INSTALLER_HASH
    
    print(f"\n📥 Python {config.System.PYTHON_VERSION_SHORT} indiriliyor...")
    print("   Bu işlem internet hızınıza bağlı olarak birkaç dakika sürebilir.\n")
    
    # Python 3.13 installer URL (64-bit)
    # En güncel 3.13 sürümü
    url = config.System.PYTHON_INSTALLER_URL
    
    try:
        # Geçici dosyaya indir
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, config.System.PYTHON_INSTALLER_FILE)
        
        # İndirme progress göster
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 // total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   İndiriliyor: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, installer_path, report_progress)
        print()  # Yeni satır
        
        # ---------------------------------------------------------
        # GÜVENLİK KONTROLÜ (SHA-256 Checksum)
        # ---------------------------------------------------------
        print("🔒 Dosya doğrulanıyor...")
        sha256_hash = hashlib.sha256()
        with open(installer_path, "rb") as f:
            # 4K chunk'lar halinde oku
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        calculated_hash = sha256_hash.hexdigest()
        
        if calculated_hash != EXPECTED_HASH:
            print("\n❌ GÜVENLİK HATASI: İndirilen dosya doğrulanamadı!")
            print(f"   Beklenen Hash: {EXPECTED_HASH}")
            print(f"   Hesaplanan Hash: {calculated_hash}")
            print("   Dosya güvenliği için siliniyor.")
            
            try:
                os.remove(installer_path)
            except OSError:
                pass
                
            return False
        
        print("✅ Dosya doğrulandı.")
        # ---------------------------------------------------------

        print(f"\n🔧 Python {config.System.PYTHON_VERSION_SHORT} yükleniyor...")
        print("   Bu işlem birkaç dakika sürebilir, lütfen bekleyin.\n")
        
        # Sessiz yükleme (PATH'e eklemeden, sadece py launcher ile kullanılacak)
        result = subprocess.run([
            installer_path,
            '/quiet',
            'InstallAllUsers=0',
            'PrependPath=0',
            'Include_launcher=1',
            'Include_pip=1'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Python {config.System.PYTHON_VERSION_SHORT} başarıyla yüklendi!\n")
            return True
        else:
            print(f"❌ Yükleme başarısız oldu. Hata kodu: {result.returncode}")
            if result.stderr:
                print(f"   Hata: {result.stderr}")
            return False
            
    except urllib.error.URLError as e:
        print(f"\n❌ İndirme başarısız: {e}")
        print("   İnternet bağlantınızı kontrol edin veya aşağıdaki adresten manuel indirin:")
        print(f"   {url}")
        return False
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        return False


def handle_python_version_fallback():
    """Python 3.14+ için 3.13'e otomatik geçiş yapar."""
    
    # Recursion Guard: Prevent infinite restart loops
    restart_attempt = int(os.environ.get("APP_RESTART_ATTEMPT", "0"))
    if restart_attempt >= 2:
        print("\n" + "!"*60)
        print("❌ KRİTİK HATA: Maksimum yeniden başlatma denemesine ulaşıldı.")
        print("!"*60)
        print("\nUygulama Python sürümleri arasında geçiş yaparken döngüye girdi.")
        print("Olası nedenler:")
        print("1. 'windows-curses' yüklemesi sessizce başarısız oluyor.")
        print("2. Algılanan Python 3.13 kurulumu hatalı.")
        print(f"\nLütfen uygulamayı doğrudan Python {config.System.PYTHON_VERSION_SHORT} ile başlatmayı deneyin:")
        print(f"   py -{config.System.PYTHON_VERSION_SHORT} main.py")
        print("-" * 60)
        input("\nÇıkmak için Enter'a basın...")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("⚠️  PYTHON SÜRÜM UYUMSUZLUĞU TESPİT EDİLDİ")
    print("="*60)
    print("\nBu uygulama 'curses' kütüphanesini kullanmaktadır.")
    print("Ancak 'windows-curses' paketi henüz Python 3.14+ desteklemiyor.")
    print(f"\nÇözüm: Python {config.System.PYTHON_VERSION_SHORT} ile çalıştırmak.")
    print("-"*60)
    
    # py launcher var mı kontrol et
    try:
        py_check = subprocess.run(
            ['py', '--version'],
            capture_output=True,
            text=True
        )
        if py_check.returncode != 0:
            raise FileNotFoundError("py launcher bulunamadı")
    except FileNotFoundError:
        print("\n❌ 'py' launcher bulunamadı.")
        print("   Python'u python.org'dan yeniden yüklemeniz gerekebilir.")
        input("\nÇıkmak için Enter...")
        return False
    
    # Python 3.13 yüklü mü kontrol et
    py313_check = subprocess.run(
        ['py', f'-{config.System.PYTHON_VERSION_SHORT}', '--version'],
        capture_output=True,
        text=True
    )
    
    if py313_check.returncode == 0:
        # 3.13 zaten yüklü - SESSIZCE GECIS YAP (mesaj yok, Enter yok)
        script_path = get_script_path()
        try:
            # Recursion Guard: Increment attempt counter
            env = os.environ.copy()
            env["APP_RESTART_ATTEMPT"] = str(restart_attempt + 1)

            result = subprocess.run(
                ['py', f'-{config.System.PYTHON_VERSION_SHORT}', script_path],
                cwd=os.path.dirname(script_path),
                env=env
            )
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            # Parent process Ctrl+C yakalarsa sessizce ve temiz çık (Check 1)
            from ui_utils import OSUtils
            try:
                # Burasi genellikle gorunmez ama ne olur ne olmaz
                OSUtils.clear_screen()
            except:
                pass
            print(f"\n{config.UI.MSG_EXIT}\n\n")
            sys.exit(0)
    else:
        # 3.13 yüklü değil - kullanıcıya sor
        print(f"\n❓ Python {config.System.PYTHON_VERSION_SHORT} sisteminizde bulunamadı.")
        print(f"\nPython {config.System.PYTHON_VERSION_SHORT} otomatik olarak yüklensin mi?")
        print("   • Python 3.14 ana sürümünüz olarak kalacak")
        print(f"   • Sadece bu uygulama için {config.System.PYTHON_VERSION_SHORT} kullanılacak")
        print("   • İnternet bağlantısı gerekli (~30 MB)")
        print()
        
        while True:
            response = input(f"Python {config.System.PYTHON_VERSION_SHORT} yüklensin mi? (E/H): ").strip().lower()
            if response in ('e', 'evet', 'y', 'yes'):
                if not install_python_313_silent():
                    input("\nÇıkmak için Enter...")
                    return False
                break
            elif response in ('h', 'hayir', 'n', 'no'):
                print("\n❌ Yükleme iptal edildi.")
                print(f"   Manuel olarak Python {config.System.PYTHON_VERSION_SHORT} yükleyebilirsiniz:")
                print("   https://www.python.org/downloads/release/python-31311/")
                input("\nÇıkmak için Enter...")
                return False
            else:
                print("   Lütfen 'E' (Evet) veya 'H' (Hayır) girin.")
    
    # Python 3.13 ile yeniden başlat
    print(f"\n🔄 Uygulama Python {config.System.PYTHON_VERSION_SHORT} ile yeniden başlatılıyor...\n")
    
    script_path = get_script_path()
    
    # Windows'ta os.execvp çalışmayabilir, subprocess kullan
    try:
        # Mevcut process'i sonlandır ve yeni process başlat
        # Recursion Guard: Increment attempt counter
        env = os.environ.copy()
        env["APP_RESTART_ATTEMPT"] = str(restart_attempt + 1)
        
        result = subprocess.run(
            ['py', f'-{config.System.PYTHON_VERSION_SHORT}', script_path],
            cwd=os.path.dirname(script_path),
            env=env
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # Parent process Ctrl+C yakalarsa sessizce ve temiz çık
        from ui_utils import OSUtils
        try:
            OSUtils.clear_screen()
        except:
            pass
        print("\nProgramdan çıkıldı. İyi günler dilerim. ❄︎\n\n")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Yeniden başlatma hatası: {e}")
        input("\nÇıkmak için Enter...")
        return False


def ensure_curses():
    """Windows'ta curses modülü yoksa otomatik olarak yükler.
    
    Python 3.14+ için windows-curses desteği yoksa, otomatik olarak
    Python {config.System.PYTHON_VERSION_SHORT}'e geçiş yaparak sorunu çözer.
    """
    # 1. Önce curses'ı kontrol et
    try:
        import curses
        return True
    except ImportError:
        pass
    
    # 2. Windows değilse hata ver
    if os.name != 'nt':
        print(f"❌ {config.UI.MSG_CURSES_NOT_FOUND}")
        return False
    
    # 3. Windows'ta windows-curses yüklemeyi dene
    print("🔧 Windows için gerekli bileşen yükleniyor (windows-curses)...")
    print("   Bu işlem sadece ilk çalıştırmada yapılır.\n")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', config.System.PKG_WINDOWS_CURSES, '--quiet'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Yükleme başarılı! Uygulama başlatılıyor...\n")
            return True
        
        # 4. Yükleme başarısız - Python sürüm sorunu olabilir
        # "No matching distribution found" hatası Python 3.14+ sorununu gösterir
        stderr_lower = result.stderr.lower()
        if "no matching distribution" in stderr_lower or "from versions: none" in stderr_lower:
            # Python 3.14+ için windows-curses desteği yok
            # Otomatik olarak Python 3.13'e geçiş yap
            return handle_python_version_fallback()
        else:
            # Başka bir hata
            print(f"❌ Yükleme başarısız: {result.stderr}")
            print("   Manuel olarak şu komutu çalıştırın:")
            print(f"   py -m pip install {config.System.PKG_WINDOWS_CURSES}")
            input("\nÇıkmak için Enter...")
            return False
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("   Manuel olarak şu komutu çalıştırın:")
        print(f"   py -m pip install {config.System.PKG_WINDOWS_CURSES}")
        input("\nÇıkmak için Enter...")
        return False


def main():
    # Windows'ta curses modülünü kontrol et ve gerekirse yükle
    if not ensure_curses():
        return
    
    # 0. Başlangıç Temizliği
    # Önceki terminal artıklarını sil
    from ui_utils import OSUtils
    OSUtils.clear_screen()
    
    # Force UTF-8 encoding for stdout/stdin to ensure emojis render correctly
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    try:
        # Pencereni genişlet (110x30)
        from ui_utils import OSUtils
        OSUtils.resize_terminal(config.Layout.TARGET_HEIGHT, config.Layout.TARGET_WIDTH)

        # controller'ı burada import et (curses yüklendikten sonra)
        import controller
        controller.run_controller()
    except KeyboardInterrupt:
        # Çıkış Temizliği
        # Simsiyah ekran/artık sorununu çözmek için ekranı temizle
        try:
            OSUtils.clear_screen()
        except:
            pass
        print(f"\n{config.UI.MSG_EXIT}\n\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {e}")
        input("Çıkmak için Enter...")

if __name__ == "__main__":
    main()