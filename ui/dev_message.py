# -*- coding: utf-8 -*-
"""
Geliştirici Mesajı Ekranı
ESC+vao tuş kombinasyonu ile açılan özel ekran.
Ciddi, sinematik, statik tasarım.
"""
import os
import curses
import textwrap
import config
from ui.colors import init_colors


def load_developer_message():
    """developer_message.txt dosyasından mesajı yükler."""
    message_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.System.FILENAME_DEV_MESSAGE)
    try:
        with open(message_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Geliştirici mesajı bulunamadı.\n\n{config.System.FILENAME_DEV_MESSAGE} dosyası oluşturulmalı."
    except Exception as e:
        return f"Mesaj yüklenirken hata: {e}"


class DeveloperMessageScreen:
    """Geliştirici mesajı ekranı — ciddi, statik tasarım."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.scroll_offset = 0
        
        curses.curs_set(0)
        self.stdscr.keypad(True)
        init_colors()
        
        self.raw_message = load_developer_message()
    
    def draw_box(self, y, x, height, width, title=""):
        """Unicode çerçeve çizer."""
        tl, tr, bl, br = '╔', '╗', '╚', '╝'
        h_line, v_line = '═', '║'
        
        top = tl + h_line * (width - 2) + tr
        bottom = bl + h_line * (width - 2) + br
        
        try:
            self.stdscr.addstr(y, x, top[:width], curses.color_pair(config.Colors.CYAN))
            
            if title:
                title_text = f" {title} "
                title_x = x + (width - len(title_text)) // 2
                self.stdscr.addstr(y, title_x, title_text,
                                   curses.color_pair(config.Colors.YELLOW) | curses.A_BOLD)
            
            for i in range(1, height - 1):
                if y + i < curses.LINES - 1:
                    self.stdscr.addstr(y + i, x, v_line, curses.color_pair(config.Colors.CYAN))
                    self.stdscr.addstr(y + i, x + width - 1, v_line, curses.color_pair(config.Colors.CYAN))
            
            if y + height - 1 < curses.LINES:
                self.stdscr.addstr(y + height - 1, x, bottom[:width], curses.color_pair(config.Colors.CYAN))
        except curses.error:
            pass
    
    def prepare_lines(self, content_width):
        """Mesajı terminale sığacak şekilde satırlara ayırır."""
        wrapped_lines = []
        for raw_line in self.raw_message.split('\n'):
            raw_line = raw_line.rstrip()
            if raw_line == '':
                wrapped_lines.append('')
            else:
                sub_lines = textwrap.wrap(raw_line, width=content_width,
                                          break_long_words=False,
                                          break_on_hyphens=False)
                if not sub_lines:
                    wrapped_lines.append('')
                else:
                    wrapped_lines.extend(sub_lines)
        return wrapped_lines
    
    def render_line(self, y, x, line, content_width):
        """Beyaz metin, @brkeyp cyan vurgulu."""
        if not line:
            return
        try:
            if '@brkeyp' in line:
                parts = line.split('@brkeyp')
                col = x
                for i, part in enumerate(parts):
                    if col < x + content_width:
                        self.stdscr.addstr(y, col, part[:x + content_width - col],
                                           curses.color_pair(config.Colors.WHITE))
                        col += len(part)
                    if i < len(parts) - 1 and col < x + content_width:
                        tag = '@brkeyp'
                        self.stdscr.addstr(y, col, tag[:x + content_width - col],
                                           curses.color_pair(config.Colors.CYAN) | curses.A_BOLD)
                        col += len(tag)
            else:
                self.stdscr.addstr(y, x, line[:content_width],
                                   curses.color_pair(config.Colors.WHITE))
        except curses.error:
            pass
    
    def draw_screen(self, lines, box_y, box_x, box_height, box_width,
                    content_x, content_width, visible_height):
        """Ekranı çizer."""
        self.stdscr.erase()
        
        # Çerçeve
        self.draw_box(box_y, box_x, box_height, box_width, "GELİŞTİRİCİDEN MESAJ")
        
        # İçerik
        total_lines = len(lines)
        max_offset = max(0, total_lines - visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
        
        for i in range(visible_height):
            line_idx = self.scroll_offset + i
            if line_idx >= total_lines:
                break
            row = box_y + 2 + i
            if row >= box_y + box_height - 1:
                break
            self.render_line(row, content_x, lines[line_idx], content_width)
        
        # Kaydırma göstergesi (sağ kenarda, kutunun içinde)
        if total_lines > visible_height:
            scroll_track_height = visible_height
            thumb_size = max(1, int(visible_height * visible_height / total_lines))
            thumb_pos = int(self.scroll_offset / max(1, max_offset) * (scroll_track_height - thumb_size))
            
            indicator_x = box_x + box_width - 2
            for i in range(scroll_track_height):
                row = box_y + 2 + i
                if row >= box_y + box_height - 1:
                    break
                try:
                    if thumb_pos <= i < thumb_pos + thumb_size:
                        self.stdscr.addstr(row, indicator_x, '█',
                                           curses.color_pair(config.Colors.CYAN))
                    else:
                        self.stdscr.addstr(row, indicator_x, '│',
                                           curses.color_pair(config.Colors.CYAN) | curses.A_DIM)
                except curses.error:
                    pass
            
            try:
                if self.scroll_offset > 0:
                    self.stdscr.addstr(box_y + 1, indicator_x, '▲',
                                       curses.color_pair(config.Colors.YELLOW))
                if self.scroll_offset < max_offset:
                    self.stdscr.addstr(box_y + box_height - 2, indicator_x, '▼',
                                       curses.color_pair(config.Colors.YELLOW))
            except curses.error:
                pass
        
        # Alt bilgi — kutunun DIŞINDA (en alt satır)
        footer = "↑↓ · Fare: Kaydır  ·  Enter / ESC: Çık"
        footer_y = box_y + box_height  # kutunun hemen altı
        if footer_y >= curses.LINES:
            footer_y = curses.LINES - 1
        footer_x = (box_width - len(footer)) // 2
        try:
            self.stdscr.addstr(footer_y, max(0, footer_x), footer, curses.A_DIM)
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def run(self):
        """Ana ekran döngüsü."""
        height, width = self.stdscr.getmaxyx()
        
        # Kutu pencereye tam otursun
        box_x = 0
        box_width = width
        box_y = 0
        box_height = height - 1  # en alta footer için 1 satır bırak
        
        content_x = 2
        content_width = box_width - 5  # sol 2 + sağda scroll göstergesi 3
        visible_height = box_height - 3  # üst border + başlık + alt border
        
        lines = self.prepare_lines(content_width)
        
        # Giriş: çerçeve çizilir, kısa bekleme
        self.stdscr.erase()
        self.draw_box(box_y, box_x, box_height, box_width, "GELİŞTİRİCİDEN MESAJ")
        self.stdscr.refresh()
        curses.napms(400)
        
        # İlk çizim
        self.draw_screen(lines, box_y, box_x, box_height, box_width,
                         content_x, content_width, visible_height)
        
        # Girdi döngüsü
        self.stdscr.nodelay(False)
        while True:
            key = self.stdscr.getch()
            
            if key in (27, ord('q'), ord('Q'), 10, 13):
                break
            
            elif key == curses.KEY_UP:
                if self.scroll_offset > 0:
                    self.scroll_offset -= 1
                    self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                     content_x, content_width, visible_height)
            
            elif key == curses.KEY_DOWN:
                max_offset = max(0, len(lines) - visible_height)
                if self.scroll_offset < max_offset:
                    self.scroll_offset += 1
                    self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                     content_x, content_width, visible_height)
            
            elif key == curses.KEY_PPAGE:
                self.scroll_offset = max(0, self.scroll_offset - visible_height)
                self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                 content_x, content_width, visible_height)
            
            elif key == curses.KEY_NPAGE:
                max_offset = max(0, len(lines) - visible_height)
                self.scroll_offset = min(max_offset, self.scroll_offset + visible_height)
                self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                 content_x, content_width, visible_height)
            
            elif key == curses.KEY_HOME:
                self.scroll_offset = 0
                self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                 content_x, content_width, visible_height)
            
            elif key == curses.KEY_END:
                max_offset = max(0, len(lines) - visible_height)
                self.scroll_offset = max_offset
                self.draw_screen(lines, box_y, box_x, box_height, box_width,
                                 content_x, content_width, visible_height)


def show_developer_message(stdscr):
    """Geliştirici mesajı ekranını gösterir."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    
    screen = DeveloperMessageScreen(stdscr)
    screen.run()
