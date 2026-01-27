# -*- coding: utf-8 -*-
import curses

class DependencyManifest:
    """Manages external tool dependencies and versioning."""
    
    # Target Platform
    TARGET_MAJOR = 3
    TARGET_MINOR = 13
    
    # Minimum Viable Version (SemVer)
    # We accept any 3.13.x where x >= MIN_PATCH.
    # This ensures we can enforce security updates (e.g. 3.13.11+) without breaking
    # the bootstrapper for every single minor release, while still allowing the
    # code to be "aware" of the minimum requirement.
    MIN_PATCH = 11

    # The version we *provide* if the user needs an install
    # This is the "Latest Known Good" version.
    LATEST_KNOWN_VERSION = "3.13.11"
    
    # Checksums for the LATEST_KNOWN_VERSION (Deterministic Security)
    # Key = Architecture (amd64, arm64)
    # Value = SHA-256 Hash
    INSTALLER_HASHES = {
        "amd64": "30d4654b3eac7ddfdf2682db4c8dcb490f3055f4f33c6906d6b828f680152101",
        # "arm64": "..." # Placeholder for future ARM64 support
    }
    
    @classmethod
    def get_version_str(cls):
        """Returns '3.13' style string."""
        return f"{cls.TARGET_MAJOR}.{cls.TARGET_MINOR}"
        
    @classmethod
    def get_installer_url(cls, arch="amd64"):
        """Dynamically generates the official Python FTP URL."""
        # Main Python FTP pattern: https://www.python.org/ftp/python/{version}/python-{version}-{arch}.exe
        # Note: 
        # - amd64 -> python-3.13.11-amd64.exe
        # - arm64 -> python-3.13.11-arm64.exe
        # - win32 -> python-3.13.11.exe (We treat 'win32' special if needed, but modern defaults are 64bit)
        
        version = cls.LATEST_KNOWN_VERSION
        base_url = "https://www.python.org/ftp/python"
        
        # Suffix handling based on standard Python installer naming
        suffix = f"-{arch}" if arch in ["amd64", "arm64"] else ""
        
        return f"{base_url}/{version}/python-{version}{suffix}.exe"

    @classmethod
    def get_expected_hash(cls, arch="amd64"):
        """Returns the expected SHA-256 hash for the given architecture."""
        return cls.INSTALLER_HASHES.get(arch)

class System:
    """System configuration and file paths."""
    WINDOW_TITLE_WIN = "PYTHON - YAZARAK ÖĞRENME/ÇALIŞMA SİMULATÖRÜ ☾☆"
    WINDOW_TITLE_UNIX = "PYTHON - YAZARAK ÖĞRENME/ÇALIŞMA SİMULATÖRÜ 🇹🇷"
    WINDOW_TITLE_FALLBACK = "PYTHON - YAZARAK OGRENME SIMULATORU"
    
    FILENAME_CURRICULUM = 'curriculum.json'
    FILENAME_PROGRESS = 'progress.json'
    FILENAME_PROGRESS_BACKUP = 'progress.backup.json'
    FILENAME_DEV_MESSAGE = 'developer_message.txt'
    
    # Python Installer Configuration
    # Refactored to use DependencyManifest
    PYTHON_VERSION_SHORT = DependencyManifest.get_version_str()
    # PYTHON_VERSION_FULL removed; use DependencyManifest.LATEST_KNOWN_VERSION
    # PYTHON_INSTALLER_HASH removed; use DependencyManifest.get_expected_hash()
    # PYTHON_INSTALLER_URL removed; use DependencyManifest.get_installer_url()
    
    # Legacy constant kept for filename if needed, or derived dynamically
    PYTHON_INSTALLER_FILE = f"python-{DependencyManifest.LATEST_KNOWN_VERSION}-amd64.exe" # Default for temp file renaming
    
    PKG_WINDOWS_CURSES = "windows-curses"

class Layout:
    """Screen dimensions and layout constants."""
    MIN_WIDTH = 20
    MIN_HEIGHT = 10
    
    TARGET_WIDTH = 110
    TARGET_HEIGHT = 30
    
    GUTTER_WIDTH = 12
    LABEL_WIDTH = 12
    
    # Scroll/Text wrap limits
    BOTTOM_MARGIN = 5 

class Timing:
    """Timeouts and delays (seconds or ms)."""
    # Seconds
    MSG_AUTOCLEAR_SEC = 3.0
    VAO_EXPIRE_SEC = 1.0
    ACTION_WAIT_SUCCESS = 1.5
    ACTION_WAIT_DEFAULT = 2.0
    
    # Milliseconds
    ESCDELAY_ENV = '25'
    ANIMATION_DELAY_FAST = 25
    ANIMATION_DELAY_NORMAL = 40
    ANIMATION_DELAY_SLOW = 100
    TYPEWRITER_DELAY = 30
    BLINK_DELAY = 300
    
    TIMEOUT_BLOCKING = -1
    TIMEOUT_QUICK = 50
    TIMEOUT_NORMAL = 100

class Colors:
    """Curses color pair IDs."""
    RED = 1      # Labels / Skipped
    CYAN = 2     # Content / Builtins
    YELLOW = 3   # Hint / Messages
    WHITE = 4    # Question Text
    MAGENTA = 5  # Keywords
    GREEN = 6    # Strings / Progress
    BLUE = 7     # Numbers
    SUCCESS = 8  # Success Badge (Green)

class UI:
    """User Interface strings and labels."""
    # Labels
    LABEL_SECTION = "BÖLÜM:"
    LABEL_TASK = "GÖREV"
    LABEL_QUESTION = "SORU:"
    LABEL_HINT = "💡 İPUCU:"
    LABEL_HINT_SHORT = "İPUCU"
    
    # Badges
    BADGE_SUCCESS = " - BAŞARILDI"
    BADGE_SKIPPED = " - ATLANDI"
    
    # Messages
    MSG_EXIT = "Programdan çıkıldı. İyi günler dilerim. ❄︎"
    MSG_RESTART_LOOP_BS = "KRİTİK HATA: Maksimum yeniden başlatma denemesine ulaşıldı."
    MSG_PYTHON_MISMATCH = "PYTHON SÜRÜM UYUMSUZLUĞU TESPİT EDİLDİ"
    MSG_CURSES_NOT_FOUND = "curses modülü bulunamadı."
    MSG_RESET_CONFIRM = "⚠️  İLERLEMEYİ SIFIRLAMAK istiyor musun? (Evet: 'e' / Hayır: 'h')"
    MSG_TASK_COMPLETED = "🔒 Bu görev tamamlandı."
    MSG_PRESS_ENTER_AGAIN = "👉 CEVABI TEKRAR GÖRMEK için tekrar Enter'a basın."
    MSG_SUBMIT_OR_TYPE = "👉 Devam etmek için yazın, GÖNDERMEK için tekrar Enter'a basın."
    MSG_SKIP_OR_TYPE = "👉 SORUYU ATLAMAK için tekrar Enter'a basın."
    
    # Celebration
    CELEBRATION_HEADER = "🎉 TEBRİKLER! TÜM GÖREVLERİ TAMAMLADINIZ! 🎉"
    CELEBRATION_SUB1 = "Python öğrenme yolculuğunda harika bir adım attın."
    CELEBRATION_SKIPPED_NOTE = "📝 Not: Bazı sorular atlanmış durumda."
    CELEBRATION_ENTER_HINT = "Atlanmış sorulara çalışmak için Enter'a bas."
    CELEBRATION_PERFECT = "Mükemmel! Hiçbir soru atlamadan tümünü başardın."

class Keys:
    """Key codes for special keys."""
    # Windows Special Keys
    WIN_ALT_LEFT = 493
    WIN_ALT_RIGHT = 492
    
    # Windows Numpad
    WIN_PAD_SLASH = 458
    WIN_PAD_ENTER = 459
    WIN_PAD_STAR = 463
    WIN_PAD_MINUS = 464
    WIN_PAD_PLUS = 465
    
    # Standard Overrides
    ENTER = 10
    RETURN = 13
    ESC = 27
    BACKSPACE_1 = 8
    BACKSPACE_2 = 127
    DELETE = 330
    CTRL_C = 3
