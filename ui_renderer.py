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
            if time.time() - editor.message_timestamp > 3:
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
        
        row = 0
        
        # Başlık
        header_line = "-" * (width - 1)
        self.stdscr.addstr(row, 0, header_line[:width-1])
        row += 1
        
        if os.name == 'nt':
            title = "PYTHON - YAZARAK ÖĞRENME/ÇALIŞMA SİMULATÖRÜ ☾☆"
        else:
            title = "PYTHON - YAZARAK ÖĞRENME/ÇALIŞMA SİMULATÖRÜ 🇹🇷"
        
        # 1. Adım: Satırı TAMAMEN temizle (Windows ghosting/artifact sorunu için en kesin çözüm)
        # erase() bazen yetersiz kalabilir, manuel boşluk basıyoruz.
        try:
            self.stdscr.addstr(row, 0, " " * (width - 1))
        except:
            pass
            
        # 2. Adım: Başlığı yaz
        try:
            self.stdscr.addstr(row, 0, title[:width-1])
        except:
            self.stdscr.addstr(row, 0, "PYTHON - YAZARAK OGRENME SIMULATORU"[:width-1])
        
        # Sayaç gösterimi (sağ üst köşe)
        # Her zaman 3 haneli ve BOŞLUKLU göster (  1,  10, 100) - Sıfırlı (001) istenmiyor.
        if editor.completed_count > 0 or editor.skipped_count > 0:
            try:
                # Sayaç parçalarını ayrı ayrı renklendir ve 3 hane formatla (Space padding)
                completed_text = f"{editor.completed_count:>3} Başarıldı"
                separator = " | "
                skipped_text = f"{editor.skipped_count:>3} Atlandı"
                
                total_len = len(completed_text) + len(separator) + len(skipped_text)
                counter_col = width - total_len - 2
                
                if counter_col > len(title) + 5:
                    # Başarıldı (yeşil)
                    self.stdscr.addstr(row, counter_col, completed_text, curses.color_pair(8) | curses.A_BOLD)
                    # Ayırıcı (normal)
                    self.stdscr.addstr(row, counter_col + len(completed_text), separator)
                    # Atlandı (kırmızı)
                    self.stdscr.addstr(row, counter_col + len(completed_text) + len(separator), skipped_text, curses.color_pair(1) | curses.A_BOLD)
            except:
                pass
        row += 1
        
        self.stdscr.addstr(row, 0, header_line[:width-1])
        row += 1
        
        # Görev Bilgisi
        row = self._draw_task_info(row, width, height, header_line)
        
        # Buffer çizimi (Kod editörü)
        buffer_start_row = row
        show_line_numbers = len(editor.buffer) > 2 or (len(editor.buffer) == 2 and len(editor.buffer[1]) > 0)
        gutter_width = 12 if show_line_numbers else 0
        
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
        
        # Footer - İnteraktif renklendirme ile
        footer_row = height - 1
        if editor.message:
            # Mesaj varsa sarı renkte göster
            try:
                self.stdscr.addstr(footer_row, 0, editor.message[:width-1], curses.color_pair(3))
            except:
                pass
        else:
            # İnteraktif footer çizimi
            is_buffer_empty = all(line.strip() == "" for line in editor.buffer)
            self.footer_renderer.draw(
                footer_row, 
                width, 
                is_buffer_empty, 
                editor.is_locked, 
                editor.task_status,
                editor.has_skipped
            )
        
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
                if row >= height - 5:
                    break
                continue
            
            wrapped = textwrap.wrap(line, width - 1) if len(line) > width - 1 else [line]
            for w_line in wrapped:
                if row >= height - 5:
                    break
                
                # Renklendirme: BÖLÜM/GÖREV kırmızı etiket + turkuvaz içerik
                try:
                    if w_line.startswith("BÖLÜM:"):
                        # "BÖLÜM:" kırmızı, geri kalanı turkuvaz (12 karakter hizalama)
                        raw_label = "BÖLÜM:"
                        label = raw_label.ljust(12)
                        content = w_line[len(raw_label):].lstrip()
                        self.stdscr.addstr(row, 0, label, curses.color_pair(1) | curses.A_BOLD)
                        self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(2) | curses.A_BOLD)
                    elif w_line.startswith("GÖREV"):
                        # "GÖREV XXX:" kısmını bul, kırmızı yap, gerisini turkuvaz (12 karakter hizalama)
                        # Damga varsa renklendir: BAŞARILDI=yeşil, ATLANDI=kırmızı
                        colon_idx = w_line.find(":")
                        if colon_idx != -1:
                            raw_label = w_line[:colon_idx+1]
                            label = raw_label.ljust(12)
                            content = w_line[colon_idx+1:].lstrip()
                            self.stdscr.addstr(row, 0, label, curses.color_pair(1) | curses.A_BOLD)
                            
                            # Damga kontrolü
                            if " - BAŞARILDI" in content:
                                # İçeriği damgadan ayır
                                badge_idx = content.find(" - BAŞARILDI")
                                main_content = content[:badge_idx]
                                badge = " - BAŞARILDI"
                                self.stdscr.addstr(row, len(label), main_content[:width-1-len(label)], curses.color_pair(2) | curses.A_BOLD)
                                badge_col = len(label) + len(main_content)
                                if badge_col + len(badge) < width:
                                    self.stdscr.addstr(row, badge_col, badge, curses.color_pair(8) | curses.A_BOLD)
                            elif " - ATLANDI" in content:
                                # İçeriği damgadan ayır
                                badge_idx = content.find(" - ATLANDI")
                                main_content = content[:badge_idx]
                                badge = " - ATLANDI"
                                self.stdscr.addstr(row, len(label), main_content[:width-1-len(label)], curses.color_pair(2) | curses.A_BOLD)
                                badge_col = len(label) + len(main_content)
                                if badge_col + len(badge) < width:
                                    self.stdscr.addstr(row, badge_col, badge, curses.color_pair(1) | curses.A_BOLD)
                            else:
                                self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(2) | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(row, 0, w_line[:width-1], curses.color_pair(1) | curses.A_BOLD)
                    elif w_line.startswith("SORU:"):
                        # SORU öncesi separator çizgisi
                        self.stdscr.addstr(row, 0, header_line[:width-1])
                        row += 1
                        if row >= height - 5:
                            break
                        # "SORU:" kırmızı, içerik beyaz (12 karakter hizalama)
                        raw_label = "SORU:"
                        label = raw_label.ljust(12)
                        content = w_line[len(raw_label):].lstrip()
                        self.stdscr.addstr(row, 0, label, curses.color_pair(1) | curses.A_BOLD)
                        self.stdscr.addstr(row, len(label), content[:width-1-len(label)], curses.color_pair(4))
                        in_soru_block = True
                    elif in_soru_block:
                        # SORU devam satırları - beyaz (12 karakter hizalama)
                        indent = " " * 12
                        self.stdscr.addstr(row, 0, indent + w_line[:width-1-12], curses.color_pair(4))
                    else:
                        # Diğer satırlar turkuvaz
                        self.stdscr.addstr(row, 0, w_line[:width-1], curses.color_pair(2))
                except:
                    pass
                row += 1
        
        # İpucu
        if editor.footer_state.show_hint and editor.hint_text:
            row += 1
            hint_text = f"💡 İPUCU: {editor.hint_text}"
            wrapped = textwrap.wrap(hint_text, width - 1)
            for h_line in wrapped:
                if row >= height - 5:
                    break
                try:
                    self.stdscr.addstr(row, 0, h_line[:width-1], curses.color_pair(3))
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
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(6))
                elif part.isdigit():
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(7))
                elif part in self.KEYWORDS:
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(5) | curses.A_BOLD)
                elif part in self.BUILTINS:
                    self.stdscr.addstr(row, col, display_part, curses.color_pair(2))
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
            "🎉 TEBRİKLER! TÜM GÖREVLERİ TAMAMLADINIZ! 🎉",
            "",
            "Python öğrenme yolculuğunda harika bir adım attın.",
            "",
        ]
        
        if editor.has_skipped:
            messages.extend([
                "📝 Not: Bazı sorular atlanmış durumda.",
                "Atlanmış sorulara çalışmak için Enter'a bas.",
            ])
        else:
            messages.append("Mükemmel! Hiçbir soru atlamadan tümünü başardın.")
        
        for msg in messages:
            if row >= height - 5:
                break
            try:
                if "TEBRİKLER" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(8) | curses.A_BOLD)
                elif "Not:" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(3))
                elif "Mükemmel" in msg:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(8) | curses.A_BOLD)
                else:
                    self.stdscr.addstr(row, 0, msg[:width-1], curses.color_pair(2))
            except:
                pass
            row += 1
        
        # Separator çizgisi
        row += 1
        self.stdscr.addstr(row, 0, header_line[:width-1])
        row += 1
        
        return row
