# -*- coding: utf-8 -*-
"""
UI Yardımcı Fonksiyonları
Terminal ve OS işlemleri için utility class.
"""
import sys
import os


class OSUtils:
    """İşletim sistemi ve terminal yardımcı fonksiyonları."""
    
    @staticmethod
    def clear_screen():
        """Terminal ekranını temizler."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def get_terminal_size():
        """Terminal boyutunu döndürür (columns, lines)."""
        try:
            columns, lines = os.get_terminal_size()
            return columns, lines
        except OSError:
            return 80, 24

    @staticmethod
    def resize_terminal(rows=30, cols=110):
        """Terminal pencere boyutunu değiştirmeyi dener (Unix/Windows ANSI destekli)."""
        sys.stdout.write(f"\x1b[8;{rows};{cols}t")
        sys.stdout.flush()
