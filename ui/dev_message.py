# -*- coding: utf-8 -*-
"""
Geliştirici Mesajı Ekranı
ESC+vao tuş kombinasyonu ile açılan özel ekran.
Animasyon efektleri ve geliştirici mesajı gösterimi.
"""
import os
import curses
import config
from ui.colors import init_colors


def load_developer_message():
    """developer_message.txt dosyasından mesajı yükler."""
    message_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.System.FILENAME_DEV_MESSAGE)
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Geliştirici mesajı bulunamadı.\n\n{config.System.FILENAME_DEV_MESSAGE} dosyası oluşturulmalı."
    except Exception as e:
        return f"Mesaj yüklenirken hata: {e}"


class DeveloperMessageScreen:
    """Geliştirici mesajı ve animasyon demo ekranı."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.scroll_offset = 0
        
        # Curses ayarları
        curses.curs_set(0)  # Cursor gizle
        self.stdscr.keypad(True)
        
        # Renk çiftleri (merkezi modülden)
        init_colors()
    
    def draw_box(self, y, x, height, width, title=""):
        """Unicode çerçeve çizer."""
        # Köşeler ve kenarlar
        tl, tr, bl, br = '╔', '╗', '╚', '╝'
        h_line, v_line = '═', '║'
        
        # Üst kenar
        top = tl + h_line * (width - 2) + tr
        bottom = bl + h_line * (width - 2) + br
        
        try:
            self.stdscr.addstr(y, x, top[:width], curses.color_pair(config.Colors.CYAN))
            
            # Başlık (varsa)
            if title:
                title_text = f" {title} "
                title_x = x + (width - len(title_text)) // 2
                self.stdscr.addstr(y, title_x, title_text, curses.color_pair(config.Colors.YELLOW) | curses.A_BOLD)
            
            # Yan kenarlar
            for i in range(1, height - 1):
                if y + i < curses.LINES - 1:
                    self.stdscr.addstr(y + i, x, v_line, curses.color_pair(config.Colors.CYAN))
                    self.stdscr.addstr(y + i, x + width - 1, v_line, curses.color_pair(config.Colors.CYAN))
            
            # Alt kenar
            if y + height - 1 < curses.LINES:
                self.stdscr.addstr(y + height - 1, x, bottom[:width], curses.color_pair(config.Colors.CYAN))
        except curses.error:
            pass
    
    def typewriter_effect(self, y, x, text, delay_ms=config.Timing.TYPEWRITER_DELAY, color=0):
        """Typewriter (daktilo) efekti - harf harf yazar."""
        for i, char in enumerate(text):
            if x + i >= curses.COLS - 1:
                break
            try:
                self.stdscr.addstr(y, x + i, char, color)
                self.stdscr.refresh()
                curses.napms(delay_ms)
            except curses.error:
                pass
    
    def fade_in_text(self, y, x, text, color_pair=config.Colors.WHITE):
        """Fade-in efekti simülasyonu (DIM -> NORMAL -> BOLD)."""
        stages = [curses.A_DIM, curses.A_NORMAL, curses.A_BOLD]
        for attr in stages:
            try:
                self.stdscr.addstr(y, x, text[:curses.COLS - x - 1], curses.color_pair(color_pair) | attr)
                self.stdscr.refresh()
                curses.napms(200)
            except curses.error:
                pass
    
    def scroll_text_up(self, y, x, lines, width, delay_ms=100):
        """Metin yukarı kayarak görünür."""
        for i, line in enumerate(lines):
            try:
                # Önceki satırları yukarı kaydır
                for j in range(min(i, 5)):
                    prev_y = y + j
                    if prev_y < curses.LINES - 2:
                        self.stdscr.addstr(prev_y, x, lines[i - 5 + j][:width], curses.color_pair(config.Colors.WHITE))
                
                # Yeni satırı ekle
                display_y = y + min(i, 4)
                if display_y < curses.LINES - 2:
                    self.stdscr.addstr(display_y, x, line[:width], curses.color_pair(config.Colors.GREEN) | curses.A_BOLD)
                
                self.stdscr.refresh()
                curses.napms(delay_ms)
            except curses.error:
                pass
    
    def progress_bar_animation(self, y, x, width, duration_ms=2000):
        """Animasyonlu progress bar."""
        steps = width - 2
        delay = duration_ms // steps
        
        try:
            # Çerçeve
            self.stdscr.addstr(y, x, '[' + ' ' * steps + ']', curses.color_pair(config.Colors.WHITE))
            self.stdscr.refresh()
            
            for i in range(steps):
                bar = '█' * (i + 1) + '░' * (steps - i - 1)
                percent = int((i + 1) / steps * 100)
                self.stdscr.addstr(y, x, f'[{bar}] {percent:3d}%', curses.color_pair(config.Colors.GREEN))
                self.stdscr.refresh()
                curses.napms(delay)
        except curses.error:
            pass
    
    def blink_text(self, y, x, text, times=3, delay_ms=config.Timing.BLINK_DELAY):
        """Yanıp sönen metin efekti."""
        for _ in range(times):
            try:
                # Göster
                self.stdscr.addstr(y, x, text[:curses.COLS - x - 1], curses.color_pair(config.Colors.YELLOW) | curses.A_BOLD)
                self.stdscr.refresh()
                curses.napms(delay_ms)
                
                # Gizle
                self.stdscr.addstr(y, x, ' ' * len(text), curses.A_NORMAL)
                self.stdscr.refresh()
                curses.napms(delay_ms // 2)
            except curses.error:
                pass
        
        # Son olarak göster
        try:
            self.stdscr.addstr(y, x, text[:curses.COLS - x - 1], curses.color_pair(config.Colors.YELLOW) | curses.A_BOLD)
        except curses.error:
            pass
    
    def rainbow_text(self, y, x, text):
        """Gökkuşağı renkli metin."""
        colors = [config.Colors.RED, config.Colors.YELLOW, config.Colors.GREEN, config.Colors.CYAN, config.Colors.BLUE, config.Colors.MAGENTA]  # Kırmızı, Sarı, Yeşil, Cyan, Mavi, Magenta
        for i, char in enumerate(text):
            if x + i >= curses.COLS - 1:
                break
            try:
                color = colors[i % len(colors)]
                self.stdscr.addstr(y, x + i, char, curses.color_pair(color) | curses.A_BOLD)
            except curses.error:
                pass
    
    def run_demo(self):
        """Animasyon demo ekranını çalıştırır."""
        height, width = self.stdscr.getmaxyx()
        
        self.stdscr.clear()
        
        # Ana çerçeve
        box_width = min(width - 4, 80)
        box_height = min(height - 2, 30)
        box_x = (width - box_width) // 2
        box_y = 1
        
        self.draw_box(box_y, box_x, box_height, box_width, "GELİŞTİRİCİDEN MESAJ")
        self.stdscr.refresh()
        curses.napms(300)
        
        content_x = box_x + 3
        content_width = box_width - 6
        row = box_y + 2
        
        # 1. TYPEWRITER EFEKTİ
        self.typewriter_effect(row, content_x, "1. TYPEWRITER EFEKTİ:", delay_ms=config.Timing.ANIMATION_DELAY_NORMAL, color=curses.color_pair(config.Colors.RED) | curses.A_BOLD)
        row += 1
        self.typewriter_effect(row, content_x, "   Merhaba! Bu metin harf harf yazılıyor...", delay_ms=config.Timing.ANIMATION_DELAY_FAST, color=curses.color_pair(config.Colors.WHITE))
        row += 2
        
        # 2. FADE-IN EFEKTİ
        try:
            self.stdscr.addstr(row, content_x, "2. FADE-IN EFEKTİ:", curses.color_pair(config.Colors.RED) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        self.fade_in_text(row, content_x + 3, "Bu metin soluktan netleşiyor!", color_pair=config.Colors.GREEN)
        row += 2
        
        # 3. PROGRESS BAR
        try:
            self.stdscr.addstr(row, content_x, "3. PROGRESS BAR:", curses.color_pair(config.Colors.RED) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        self.progress_bar_animation(row, content_x + 3, min(40, content_width - 10), duration_ms=1500)
        row += 2
        
        # 4. YANIP SÖNEN METİN
        try:
            self.stdscr.addstr(row, content_x, "4. YANIP SÖNEN METİN:", curses.color_pair(config.Colors.RED) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        self.blink_text(row, content_x + 3, "DİKKAT! Bu metin yanıp sönüyor!", times=3, delay_ms=250)
        row += 2
        
        # 5. GÖKKUŞAĞI METİN
        try:
            self.stdscr.addstr(row, content_x, "5. GÖKKUŞAĞI METİN:", curses.color_pair(config.Colors.RED) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1
        self.rainbow_text(row, content_x + 3, "Her harf farkli renkte!")
        row += 2
        
        # 6. SCROLL TEXT DEMO
        if row + 7 < box_y + box_height - 2:
            try:
                self.stdscr.addstr(row, content_x, "6. KAYAN METİN:", curses.color_pair(config.Colors.RED) | curses.A_BOLD)
            except curses.error:
                pass
            row += 1
            scroll_lines = [
                "Satır 1: Python öğrenmek eğlencelidir!",
                "Satır 2: Her gün pratik yap.",
                "Satır 3: Hatalardan öğren.",
                "Satır 4: Kodlamaya devam et!",
                "Satır 5: Başarı yakın!"
            ]
            self.scroll_text_up(row, content_x + 3, scroll_lines, content_width - 6, delay_ms=150)
            row += 6
        
        self.stdscr.refresh()
        
        # Separator
        row = box_y + box_height - 4
        try:
            separator = "─" * (content_width)
            self.stdscr.addstr(row, content_x, separator[:content_width], curses.color_pair(config.Colors.CYAN))
        except curses.error:
            pass
        
        # Geliştirici mesajı
        row += 1
        message = load_developer_message()
        first_line = message.split('\n')[0] if message else ""
        try:
            self.stdscr.addstr(row, content_x, f"📝 {first_line[:content_width-4]}", curses.color_pair(config.Colors.YELLOW))
        except curses.error:
            pass
        
        # Footer
        footer_text = "Çıkmak için Enter veya ESC'ye bas"
        footer_x = box_x + (box_width - len(footer_text)) // 2
        try:
            self.stdscr.addstr(box_y + box_height - 2, footer_x, footer_text, curses.A_DIM)
        except curses.error:
            pass
        
        self.stdscr.refresh()
        
        # Çıkış için bekle
        self.stdscr.nodelay(False)
        while True:
            key = self.stdscr.getch()
            if key in (10, 13, 27, ord('q'), ord('Q')):  # Enter, ESC, q
                break


def show_developer_message(stdscr):
    """Geliştirici mesajı ekranını gösterir."""
    # Wrapper kullanma! Mevcut stdscr üzerinden devam et.
    # Cursor'ı gizle (Zaten gizli ama garanti olsun)
    try:
        curses.curs_set(0)
    except curses.error:
        pass
        
    screen = DeveloperMessageScreen(stdscr)
    screen.run_demo()
