# -*- coding: utf-8 -*-
"""
Renk Yönetimi Modülü
Curses renk çiftlerini merkezi olarak yönetir.
DRY principle: Tüm UI modülleri bu modülü kullanmalı.
"""
import curses
import config

_initialized = False


def init_colors():
    """
    Curses renk çiftlerini bir kez başlatır.
    
    Bu fonksiyon birden fazla kez çağrılabilir; sadece ilk çağrıda
    renk başlatma işlemi yapılır.
    
    Usage:
        from ui.colors import init_colors
        init_colors()
    """
    global _initialized
    
    if _initialized:
        return
    
    if not curses.has_colors():
        _initialized = True  # Even without colors, mark as initialized
        return
    
    curses.start_color()
    curses.use_default_colors()
    
    # Renk çiftleri
    curses.init_pair(config.Colors.RED, curses.COLOR_RED, -1)       # Etiketler, Atlandı
    curses.init_pair(config.Colors.CYAN, curses.COLOR_CYAN, -1)     # İçerik, Builtins
    curses.init_pair(config.Colors.YELLOW, curses.COLOR_YELLOW, -1) # İpucu, Mesaj
    curses.init_pair(config.Colors.WHITE, curses.COLOR_WHITE, -1)   # Soru
    curses.init_pair(config.Colors.SUCCESS, curses.COLOR_GREEN, -1) # Başarıldı damgası
    curses.init_pair(config.Colors.MAGENTA, curses.COLOR_MAGENTA, -1)  # Keyword
    curses.init_pair(config.Colors.GREEN, curses.COLOR_GREEN, -1)   # String
    curses.init_pair(config.Colors.BLUE, curses.COLOR_BLUE, -1)     # Number
    
    _initialized = True


def reset_colors():
    """
    Renk durumunu sıfırlar (test amaçlı).
    """
    global _initialized
    _initialized = False
