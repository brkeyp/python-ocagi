# -*- coding: utf-8 -*-
import curses

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
    PYTHON_VERSION_SHORT = "3.13"
    PYTHON_VERSION_FULL = "3.13.11"
    PYTHON_INSTALLER_HASH = "30d4654b3eac7ddfdf2682db4c8dcb490f3055f4f33c6906d6b828f680152101"
    PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe"
    PYTHON_INSTALLER_FILE = "python-3.13.11-amd64.exe"
    
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
