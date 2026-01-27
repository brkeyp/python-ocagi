# -*- coding: utf-8 -*-
"""
Editor Renderer Modülü
Ekran çizimi ve syntax highlighting işlemleri.
"""
import textwrap
import curses
import re
import time
import os
import config

from ui_footer import FooterRenderer


class EditorRenderer:
    """Editor ekran çizim işlemleri."""
    
    # Syntax highlighting için keyword ve builtin setleri
    KEYWORDS = {
        "def", "import", "from", "return", "if", "else", "elif",
        "for", "while", "class", "try", "except", "pass", "break",
        "continue", "and", "or", "not", "in", "is", "None", "True", "False"
    }
    
    BUILTINS = {
        "print", "len", "input", "str", "int", "float", "list",
        "dict", "set", "range", "enumerate", "open", "type"
    }
    
    # Syntax highlighting pattern
    SYNTAX_PATTERN = r"(#[^\n]*|\"[^\"]*\"|'[^']*'|\b\d+\b|\b\w+\b|[^\w\s])"
    
    def __init__(self, stdscr, editor):
        """
        Args:
            stdscr: Curses standard screen
            editor: Editor instance (state'e erişim için)
        """
        self.stdscr = stdscr
        self.editor = editor
        self.footer_renderer = FooterRenderer(stdscr, editor.footer_state)
    
    def refresh_screen(self):
        """Curses ile ekranı yeniden çizer."""
        editor = self.editor
        
        # Otomatik mesaj temizleme (3 saniye sonra)
        if editor.message and editor.message_timestamp:
            if time.time() - editor.message_timestamp > config.Timing.MSG_AUTOCLEAR_SEC:
                editor.message = ""
                editor.message_timestamp = None
        
        # Windows'ta cursor flashing sorununu önlemek için:
        # 1. Cursor'ı çizim sırasında gizle
        # 2. clear() yerine erase() kullan (cursor pozisyonunu korur)
        try:
            curses.curs_set(0)  # Cursor'ı gizle
        except:
            pass
        
        self.stdscr.erase()  # clear() yerine erase() - daha az flicker
        height, width = self.stdscr.getmaxyx()
        
        # 0. Min Viewport Check
        if height < config.Layout.MIN_HEIGHT or width < config.Layout.MIN_WIDTH:
            self._draw_too_small_warning(height, width)
            self.stdscr.noutrefresh()
            curses.doupdate()
            return
        
        row = 0
        
        is_compact = height < config.Layout.COMPACT_HEIGHT_THRESHOLD
        
        if os.name == 'nt':
            title = config.System.WINDOW_TITLE_WIN
        else:
            title = config.System.WINDOW_TITLE_UNIX
            
        header_line = "-" * (width - 1)

        if is_compact:
            # Compact Header: Tek satır, inverted
            # Title'ı ortala/kes
            display_title = f" {title.strip()} "
            if len(display_title) > width - 1:
                display_title = display_title[:width-4] + "..."
            
            # Center title
            start_x = max(0, (width - len(display_title)) // 2)
            try:
                self.stdscr.addstr(row, 0, " " * (width - 1), curses.A_REVERSE) # Arkaplan şeridi
                self.stdscr.addstr(row, start_x, display_title, curses.A_REVERSE | curses.A_BOLD)
            except:
                pass
            
            # Compact mode'da sayaçları başlık satırına göm (Sağ köşe)
            if editor.completed_count > 0 or editor.skipped_count > 0:
                try:
                    # Basit sayaç: "✓10 ✗5"
                    counter_text = f"✓{editor.completed_count} ✗{editor.skipped_count}"
                    if len(counter_text) + start_x + len(display_title) < width - 2:
                        self.stdscr.addstr(row, width - len(counter_text) - 2, counter_text, curses.A_REVERSE)
                except:
                    pass
            
            row += 1
            
        else:
            # Normal Header (3 Satır)
            # 1. Üst Çizgi
            self.stdscr.addstr(row, 0, header_line[:width-1])
            row += 1
            
            # 2. Başlık Satırı (Temizle + Yaz)
            try:
                self.stdscr.addstr(row, 0, " " * (width - 1))
            except:
                pass
                
            try:
                self.stdscr.addstr(row, 0, title[:width-1])
            except:
                self.stdscr.addstr(row, 0, config.System.WINDOW_TITLE_FALLBACK[:width-1])
            
            # Sayaç gösterimi (Normal)
            if editor.completed_count > 0 or editor.skipped_count > 0:
                try:
                    completed_text = f"{editor.completed_count:>3} Başarıldı"
                    separator = " | "
                    skipped_text = f"{editor.skipped_count:>3} Atlandı"
                    
                    total_len = len(completed_text) + len(separator) + len(skipped_text)
                    counter_col = width - total_len - 2
                    
                    if counter_col > len(title) + 5:
                        self.stdscr.addstr(row, counter_col, completed_text, curses.color_pair(config.Colors.SUCCESS) | curses.A_BOLD)
                        self.stdscr.addstr(row, counter_col + len(completed_text), separator)
                        self.stdscr.addstr(row, counter_col + len(completed_text) + len(separator), skipped_text, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                except:
                    pass
            row += 1
            
            # 3. Alt Çizgi
            self.stdscr.addstr(row, 0, header_line[:width-1])
            row += 1
        
        # Görev Bilgisi
        row = self._draw_task_info(row, width, height, header_line)
        
        # Buffer çizimi (Kod editörü)
        buffer_start_row = row
        show_line_numbers = len(editor.buffer) > 2 or (len(editor.buffer) == 2 and len(editor.buffer[1]) > 0)
        gutter_width = config.Layout.GUTTER_WIDTH if show_line_numbers else 0
        
        for i, line in enumerate(editor.buffer):
            if row >= height - 2:
                break
            
            prefix = ""
            if show_line_numbers:
                prefix = f"Satır {i+1}: ".ljust(gutter_width)
                try:
                    self.stdscr.addstr(row, 0, prefix, curses.A_DIM)
                except:
                    pass
            
            # Syntax highlighting
            self._draw_colorized_line(row, gutter_width, line, width)
            row += 1
        
        # Footer - İnteraktif renklendirme ile (Unified)
        footer_row = height - 1
        self.footer_renderer.draw(footer_row, width, editor)
        
        # Cursor pozisyonu
        cursor_row = buffer_start_row + editor.cy
        cursor_col = gutter_width + editor.cx
        
        if cursor_row < height - 1 and cursor_col < width:
            try:
                self.stdscr.move(cursor_row, cursor_col)
            except:
                pass
        
        # Optimized refresh: noutrefresh + doupdate for less flicker
        self.stdscr.noutrefresh()
        curses.doupdate()
        
        # Cursor'ı tekrar göster
        try:
            curses.curs_set(1)
        except:
            pass
    
    def _draw_task_info(self, row, width, height, header_line):
        """Özel içerik mod kontrolü. Celebration modunda özel ekran gösterir."""
        editor = self.editor
        
        # Celebration modunda özel mesaj göster
        if editor.task_status == "celebration":
            return self._draw_celebration_screen(row, width, height, header_line)
        
        if not editor.task_info:
            return row
        
        raw_lines = editor.task_info.split('\n')
        in_soru_block = False  # SORU içeriğini takip için
        
        for line in raw_lines:
            if not line.strip():
                # Boş satır - SORU bloğunu bitir
                in_soru_block = False
                row += 1
                if row >= height - config.Layout.BOTTOM_MARGIN:
                    break
                continue
            
            wrapped = textwrap.wrap(line, width - 1) if len(line) > width - 1 else [line]
            for w_line in wrapped:
                if row >= height - config.Layout.BOTTOM_MARGIN:
                    break
                
                # Renklendirme: BÖLÜM/GÖREV kırmızı etiket + turkuvaz içerik
                try:
                    if w_line.startswith(config.UI.LABEL_SECTION):
                        # "BÖLÜM:" kırmızı, geri kalanı turkuvaz (12 karakter hizalama)
                        raw_label = config.UI.LABEL_SECTION
                        label = raw_label.ljust(config.Layout.LABEL_WIDTH)
                        content = w_line[len(raw_label):].lstrip()
                        self.stdscr.addstr(row, 0, label, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                        self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(config.Colors.CYAN) | curses.A_BOLD)
                    elif w_line.startswith(config.UI.LABEL_TASK):
                        # "GÖREV XXX:" kısmını bul, kırmızı yap, gerisini turkuvaz (12 karakter hizalama)
                        # Damga varsa renklendir: BAŞARILDI=yeşil, ATLANDI=kırmızı
                        colon_idx = w_line.find(":")
                        if colon_idx != -1:
                            raw_label = w_line[:colon_idx+1]
                            label = raw_label.ljust(config.Layout.LABEL_WIDTH)
                            content = w_line[colon_idx+1:].lstrip()
                            self.stdscr.addstr(row, 0, label, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                            
                            # Damga kontrolü
                            if config.UI.BADGE_SUCCESS in content:
                                # İçeriği damgadan ayır
                                badge_idx = content.find(config.UI.BADGE_SUCCESS)
                                main_content = content[:badge_idx]
                                badge = config.UI.BADGE_SUCCESS
                                self.stdscr.addstr(row, len(label), main_content[:width-1-len(label)], curses.color_pair(config.Colors.CYAN) | curses.A_BOLD)
                                badge_col = len(label) + len(main_content)
                                if badge_col + len(badge) < width:
                                    self.stdscr.addstr(row, badge_col, badge, curses.color_pair(config.Colors.SUCCESS) | curses.A_BOLD)
                            elif config.UI.BADGE_SKIPPED in content:
                                # İçeriği damgadan ayır
                                badge_idx = content.find(config.UI.BADGE_SKIPPED)
                                main_content = content[:badge_idx]
                                badge = config.UI.BADGE_SKIPPED
                                self.stdscr.addstr(row, len(label), main_content[:width-1-len(label)], curses.color_pair(config.Colors.CYAN) | curses.A_BOLD)
                                badge_col = len(label) + len(main_content)
                                if badge_col + len(badge) < width:
                                    self.stdscr.addstr(row, badge_col, badge, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                            else:
                                self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(config.Colors.CYAN) | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(row, 0, w_line[:width-1], curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                    elif w_line.startswith(config.UI.LABEL_QUESTION):
                        # SORU öncesi separator çizgisi
                        self.stdscr.addstr(row, 0, header_line[:width-1])
                        row += 1
                        if row >= height - config.Layout.BOTTOM_MARGIN:
                            break
                        # "SORU:" kırmızı, içerik beyaz (12 karakter hizalama)
                        raw_label = config.UI.LABEL_QUESTION
                        label = raw_label.ljust(config.Layout.LABEL_WIDTH)
                        content = w_line[len(raw_label):].lstrip()
                        self.stdscr.addstr(row, 0, label, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                        self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(config.Colors.WHITE))
                        in_soru_block = True
                    elif in_soru_block:
                        # SORU devam satırları - beyaz (12 karakter hizalama)
                        indent = " " * config.Layout.LABEL_WIDTH
                        self.stdscr.addstr(row, 0, indent + w_line[:width-1-config.Layout.LABEL_WIDTH], curses.color_pair(config.Colors.WHITE))
                    else:
                        # Diğer satırlar turkuvaz
                        self.stdscr.addstr(row, 0, w_line[:width-1], curses.color_pair(config.Colors.CYAN))
                except:
                    pass
                row += 1
        
        # İpucu
        if editor.footer_state.show_hint and editor.hint_text:
            row += 1
            hint_text = f"{config.UI.LABEL_HINT} {editor.hint_text}"
            wrapped = textwrap.wrap(hint_text, width - 1)
            for h_line in wrapped:
                if row >= height - config.Layout.BOTTOM_MARGIN:
                    break
                try:
                    self.stdscr.addstr(row, 0, h_line[:width-1], curses.color_pair(config.Colors.YELLOW))
                except:
                    pass
                row += 1
        
        self.stdscr.addstr(row, 0, header_line[:width-1])
        row += 1
        
        return row
    
    def _draw_colorized_line(self, row, col_start, line, max_width):
        """Syntax highlighting ile satırı çizer."""
        parts = re.split(self.SYNTAX_PATTERN, line)
        
        col = col_start
        for part in parts:
            if not part:
                continue
            if col >= max_width - 1:
                break
            
            remaining = max_width - 1 - col
            display_part = part[:remaining]
            
            try:
                if part.startswith("#"):
                    self.stdscr.addstr(row, col, display_part, curses.A_DIM)
                elif part.startswith("'") or part.startswith('"'):
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(config.Colors.GREEN))
                elif part.isdigit():
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(config.Colors.BLUE))
                elif part in self.KEYWORDS:
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(config.Colors.MAGENTA) | curses.A_BOLD)
                elif part in self.BUILTINS:
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(config.Colors.CYAN))
                else:
                    self.stdscr.addstr(row, col, display_part)
            except:
                pass
            
            col += len(display_part)
    
    def _draw_celebration_screen(self, row, width, height, header_line):
        """Tebrikler ekranını çizer."""
        editor = self.editor
        
        # Tebrik mesajları
        messages = [
            config.UI.CELEBRATION_HEADER,
            "",
            config.UI.CELEBRATION_SUB1,
            "",
        ]
        
        if editor.has_skipped:
            messages.extend([
                config.UI.CELEBRATION_SKIPPED_NOTE,
                config.UI.CELEBRATION_ENTER_HINT,
            ])
        else:
            messages.append(config.UI.CELEBRATION_PERFECT)
        
        for msg in messages:
            if row >= height - config.Layout.BOTTOM_MARGIN:
                break
            try:
                if "TEBRİKLER" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(config.Colors.SUCCESS) | curses.A_BOLD)
                elif "Not:" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(config.Colors.YELLOW))
                elif "Mükemmel" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(config.Colors.SUCCESS) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(config.Colors.CYAN))
            except:
                pass
            row += 1
        
        # Separator çizgisi
        row += 1
        self.stdscr.addstr(row, 0, header_line[:width-1])
        row += 1
        
        return row
    
    def _draw_too_small_warning(self, height, width):
        """Ekran çok küçükse uyarı gösterir."""
        msg1 = "⚠️  PENCERE ÇOK KÜÇÜK"
        msg2 = f"Min Boyut: {config.Layout.MIN_WIDTH}x{config.Layout.MIN_HEIGHT}"
        msg3 = f"Mevcut: {width}x{height}"
        msg4 = "Lütfen pencereyi büyütün."
        
        cy = height // 2 - 2
        
        try:
            if cy >= 0:
                cx1 = max(0, (width - len(msg1)) // 2)
                self.stdscr.addstr(cy, cx1, msg1, curses.color_pair(config.Colors.RED) | curses.A_BOLD)
                
            if cy + 1 < height:
                cx2 = max(0, (width - len(msg2)) // 2)
                self.stdscr.addstr(cy + 1, cx2, msg2, curses.color_pair(config.Colors.YELLOW))

            if cy + 2 < height:
                cx3 = max(0, (width - len(msg3)) // 2)
                self.stdscr.addstr(cy + 2, cx3, msg3, curses.color_pair(config.Colors.YELLOW))
                
            if cy + 4 < height:
                cx4 = max(0, (width - len(msg4)) // 2)
                self.stdscr.addstr(cy + 4, cx4, msg4, curses.color_pair(config.Colors.WHITE))
        except:
            pass
