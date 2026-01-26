# -*- coding: utf-8 -*-
"""
Python Kurs Simulatörü - Ana UI Modülü
Curses tabanlı kod editörü.
"""
import sys
import os
import time
import curses
import locale

# Locale ayarı - Türkçe karakter desteği için
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

# ESCDELAY ayarı - ESC tuşunun anında tepki vermesi için
# (curses varsayılan olarak escape sequence bekler, bu gecikmeye neden olur)
os.environ.setdefault('ESCDELAY', '25')

# Alt modüllerden import
from ui_utils import OSUtils
from ui_footer import FooterState
from ui_renderer import EditorRenderer


class Editor:
    """Curses Tabanlı Çok Satırlı Terminal Editörü"""
    
    def __init__(self, stdscr, task_info="", hint_text="", initial_code="", 
                 task_status="pending", completed_count=0, skipped_count=0, has_skipped=False):
        self.stdscr = stdscr
        
        # Görev durumu ve sayaçlar
        self.task_status = task_status
        self.is_locked = (task_status == "completed")
        self.completed_count = completed_count
        self.skipped_count = skipped_count
        self.has_skipped = has_skipped
        
        # Buffer'ı initial_code ile doldur (varsa)
        if initial_code and initial_code.strip():
            self.buffer = initial_code.split('\n')
            # Cursor'ı kodun sonuna konumlandır
            self.cy = len(self.buffer) - 1
            self.cx = len(self.buffer[self.cy])
        else:
            self.buffer = [""]  # Satırlar
            self.cy = 0  # Cursor Y (Satır)
            self.cx = 0  # Cursor X (Sütun)
        
        self.waiting_for_submit = False
        
        # UX: Dinamik Mesajlar ve İpucu
        self.hint_text = hint_text
        self.message = ""
        self.message_timestamp = None  # Mesaj zamanlayıcı (otomatik kaybolma için)
        
        self.task_info = task_info
        
        # Footer state yönetimi (yeni modüler yapı)
        self.footer_state = FooterState()
        
        # Renderer oluştur
        self.renderer = EditorRenderer(stdscr, self)
        
        # Curses ayarları
        curses.curs_set(1)  # Cursor görünür
        self.stdscr.keypad(True)  # Özel tuşları etkinleştir
        self.stdscr.nodelay(False)  # Blocking mod
        
        # ESC tuşu için bekleme süresini minimize et (anında tepki için)
        try:
            curses.set_escdelay(25)  # Python 3.9+
        except AttributeError:
            pass  # Eski Python sürümlerinde env variable kullanılır
        
        # Renk çiftleri
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)      # Etiketler / Atlandı
            curses.init_pair(2, curses.COLOR_CYAN, -1)     # İçerik
            curses.init_pair(3, curses.COLOR_YELLOW, -1)   # İpucu/Mesaj
            curses.init_pair(4, curses.COLOR_WHITE, -1)    # Soru
            curses.init_pair(8, curses.COLOR_GREEN, -1)    # Başarıldı damgası
            curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Keyword
            curses.init_pair(6, curses.COLOR_GREEN, -1)    # String
            curses.init_pair(7, curses.COLOR_BLUE, -1)     # Number

    # Windows Key Codes
    KEY_ALT_LEFT_WIN = 493
    KEY_ALT_RIGHT_WIN = 492
    
    # Windows Numpad Codes
    KEY_WIN_PAD_SLASH = 458
    KEY_WIN_PAD_ENTER = 459
    KEY_WIN_PAD_STAR = 463
    KEY_WIN_PAD_MINUS = 464
    KEY_WIN_PAD_PLUS = 465

    def run(self):
        """Editörü başlatır ve kodu döndürür."""
        
        # İlk çizim için flag
        should_redraw = True
        
        while True:
            # 1. Mesaj süresi doldu mu kontrol et
            if self.message and self.message_timestamp:
                if time.time() - self.message_timestamp > 3:
                    self.message = ""
                    self.message_timestamp = None
                    should_redraw = True
            
            # 2. Highlight expire kontrolü (Footer için)
            if self.footer_state.vao_expire > 0:
                self.footer_state.check_expired()
                # Expire olduysa redraw gerekir, henüz olmadıysa beklemeye devam
                if self.footer_state.vao_progress == 0:
                     should_redraw = True
            
            # 3. Ekranı yenile (Sadece gerekirse)
            if should_redraw:
                self.renderer.refresh_screen()
                should_redraw = False
            
            # 4. Timeout Belirle
            # Eğer ekranda süreli bir mesaj veya highlight varsa kısa timeout (100ms)
            # Yoksa CPU'yu yormamak için blocking veya uzun timeout (-1 veya 1000ms)
            # Ancak animasyon akıcılığı için 100ms güvenli bir varsayılandır, 
            # asıl optimizasyon refresh_screen'i gereksiz çağırmamaktır.
            # Yine de mesaj yoksa blocking yapmak en iyisi (sifir CPU kullanımı)
            has_active_timer = (self.message is not None and self.message != "") or \
                               (self.footer_state.vao_expire > 0)
            
            if has_active_timer:
                self.stdscr.timeout(100)
            else:
                self.stdscr.timeout(-1)  # Blocking mode (tuş bekle)
            
            try:
                # get_wch() kullanarak Unicode desteği sağla
                try:
                    char = self.stdscr.get_wch()
                except AttributeError:
                    char = self.stdscr.getch()
                except curses.error:
                    # Timeout -> Loop başına dön
                    continue
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            
            # Tuş algılandı -> Bir sonraki döngüde çizim yapmalı
            should_redraw = True
            
            # char string ise Unicode karakter, int ise özel tuş
            is_char_str = isinstance(char, str)
            char_code = ord(char) if is_char_str else char
            
            # --- WINDOWS NUMPAD NORMALİZASYONU ---
            # Windows'ta Numpad tuşları karakter yerine özel integer kodlar gönderir.
            # Bunları standart karakterlere dönüştürerek editörün bunları normal yazı gibi algılamasını sağlıyoruz.
            if not is_char_str:
                if char_code == self.KEY_WIN_PAD_ENTER:
                    char = '\n'
                    is_char_str = True
                    char_code = 10
                elif char_code == self.KEY_WIN_PAD_PLUS:
                    char = '+'
                    is_char_str = True
                    char_code = 43
                elif char_code == self.KEY_WIN_PAD_MINUS:
                    char = '-'
                    is_char_str = True
                    char_code = 45
                elif char_code == self.KEY_WIN_PAD_STAR:
                    char = '*'
                    is_char_str = True
                    char_code = 42
                elif char_code == self.KEY_WIN_PAD_SLASH:
                    char = '/'
                    is_char_str = True
                    char_code = 47
            
            # --- ÇIKIŞ (Ctrl+C) ---
            if char_code == 3:  # Ctrl+C
                raise KeyboardInterrupt
                
            # --- WINDOWS ALT+ARROW FIX ---
            if char_code == self.KEY_ALT_LEFT_WIN:
                self.footer_state.reset_vao()
                return "PREV_TASK"
            
            elif char_code == self.KEY_ALT_RIGHT_WIN:
                self.footer_state.reset_vao()
                return "NEXT_TASK"

            # --- NAVİGASYON ---
            if char_code == curses.KEY_UP:
                if self.cy > 0:
                    self.cy -= 1
                    self.cx = min(self.cx, len(self.buffer[self.cy]))
                self.waiting_for_submit = False
                self.message = ""

            elif char_code == curses.KEY_DOWN:
                if self.cy < len(self.buffer) - 1:
                    self.cy += 1
                    self.cx = min(self.cx, len(self.buffer[self.cy]))
                self.waiting_for_submit = False
                self.message = ""

            elif char_code == curses.KEY_LEFT:
                if self.cx > 0:
                    self.cx -= 1
                elif self.cy > 0:
                    self.cy -= 1
                    self.cx = len(self.buffer[self.cy])
                self.waiting_for_submit = False
                self.message = ""

            elif char_code == curses.KEY_RIGHT:
                if self.cx < len(self.buffer[self.cy]):
                    self.cx += 1
                elif self.cy < len(self.buffer) - 1:
                    self.cy += 1
                    self.cx = 0
                self.waiting_for_submit = False
                self.message = ""

            # --- DÜZENLEME ---
            elif char_code in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                if self.is_locked:
                    self.message = "🔒 Bu görev tamamlandı."
                    self.message_timestamp = time.time()
                else:
                    self._handle_backspace()
                
            elif char_code in (curses.KEY_DC, 330):  # Delete tuşu
                # RESET TRIGGER (Buffer boşsa VEYA kilitli görevde)
                is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                if is_buffer_empty or self.is_locked:
                    self.message = "⚠️  İLERLEMEYİ SIFIRLAMAK istiyor musun? (Evet: 'e' / Hayır: 'h')"
                    self.renderer.refresh_screen()
                    while True:
                        confirm = self.stdscr.getch()
                        if confirm in (ord('e'), ord('E')):
                            return "RESET_ALL"
                        elif confirm in (ord('h'), ord('H')) or (confirm >= 32 and confirm < 127):
                            self.message = ""
                            break
                else:
                    self._handle_delete()

            # --- ENTER MANTIĞI ---
            elif char_code in (curses.KEY_ENTER, 10, 13) or (is_char_str and char in ('\n', '\r')):
                # Celebration modunda - atlanmış görev varsa yönlendir
                if self.task_status == "celebration":
                    if self.has_skipped:
                        return "GOTO_FIRST_SKIPPED"
                    # has_skipped=False ise Enter'a basınca hiçbir şey olmasın
                    continue
                # Kilitli görevde (completed) - sadece mesaj göster
                elif self.is_locked:
                    self.message = "🔒 Bu görev tamamlandı."
                    self.message_timestamp = time.time()
                # Atlanmış görevde
                elif self.task_status == "skipped":
                    if self.waiting_for_submit:
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        if is_buffer_empty:
                            return None  # Çözümü tekrar göster
                        else:
                            return "\n".join(self.buffer)  # Yeni cevabı gönder
                    else:
                        # İlk Enter -> Satır Böl veya Yeni Satır
                        current_line = self.buffer[self.cy]
                        left_part = current_line[:self.cx]
                        right_part = current_line[self.cx:]
                        
                        indent = ""
                        if left_part.strip().endswith(':'):
                            indent = "    "
                        
                        self.buffer[self.cy] = left_part
                        self.buffer.insert(self.cy + 1, indent + right_part)
                        self.cy += 1
                        self.cx = len(indent)
                        self.waiting_for_submit = True
                        
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        if is_buffer_empty:
                            self.message = "👉 CEVABI TEKRAR GÖRMEK için tekrar Enter'a basın."
                        else:
                            self.message = "👉 Devam etmek için yazın, GÖNDERMEK için tekrar Enter'a basın."
                # Normal (pending) görev
                else:
                    if self.waiting_for_submit:
                        # İkinci Enter geldi
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        
                        if is_buffer_empty:
                            return None  # Skip sinyali
                        else:
                            return "\n".join(self.buffer)
                    else:
                        # İlk Enter -> Satır Böl veya Yeni Satır
                        current_line = self.buffer[self.cy]
                        left_part = current_line[:self.cx]
                        right_part = current_line[self.cx:]
                        
                        # Auto-Indent Mantığı
                        indent = ""
                        if left_part.strip().endswith(':'):
                            indent = "    "
                        
                        self.buffer[self.cy] = left_part
                        self.buffer.insert(self.cy + 1, indent + right_part)
                        
                        self.cy += 1
                        self.cx = len(indent)
                        
                        self.waiting_for_submit = True
                        
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        
                        if is_buffer_empty:
                            self.message = "👉 SORUYU ATLAMAK için tekrar Enter'a basın."
                        else:
                            self.message = "👉 Devam etmek için yazın, GÖNDERMEK için tekrar Enter'a basın."

            # --- KARAKTER GİRİŞİ (Unicode dahil) ---
            elif is_char_str and len(char) == 1 and ord(char) >= 32:
                # İpucu Kontrolü (?) - kilitli görevde de çalışır
                if char == '?':
                    self.footer_state.show_hint = not self.footer_state.show_hint
                    continue
                
                # Kilitli görevde karakter girişini engelle
                if self.is_locked:
                    self.message = "🔒 Bu görev tamamlandı."
                    self.message_timestamp = time.time()
                    continue
                
                # Unicode karakter (Türkçe karakterler dahil)
                self.waiting_for_submit = False
                self.message = ""
                
                line = self.buffer[self.cy]
                self.buffer[self.cy] = line[:self.cx] + char + line[self.cx:]
                self.cx += 1
            
            elif not is_char_str and char_code >= 32 and char_code < 127:
                ch = chr(char_code)
                
                # İpucu Kontrolü (?) - kilitli görevde de çalışır
                if ch == '?':
                    self.footer_state.show_hint = not self.footer_state.show_hint
                    continue
                
                # Kilitli görevde karakter girişini engelle
                if self.is_locked:
                    self.message = "🔒 Bu görev tamamlandı."
                    self.message_timestamp = time.time()
                    continue
                
                # Eski getch() davranışı için ASCII karakter (fallback)
                self.waiting_for_submit = False
                self.message = ""
                
                line = self.buffer[self.cy]
                self.buffer[self.cy] = line[:self.cx] + ch + line[self.cx:]
                self.cx += 1
            
            # --- ESC tuşu ve Alt kombinasyonları ---
            elif char_code == 27:  # ESC
                result = self._handle_esc_sequence()
                if result:
                    return result
                should_redraw = True  # ESC basıldıysa footer değişmiştir

    def _handle_esc_sequence(self):
        """ESC tuşu ve kombinasyonlarını işler. Return değeri varsa ana döngüden çık."""
        # Mesajı temizle ki footer çizilebilsin ve highlight görünsün
        self.message = ""
        # ESC basıldı - footer'da highlight göster (ANINDA)
        self.footer_state.set_vao_progress(1)
        self.renderer.refresh_screen()
        
        # Non-blocking ile 1 saniye içinde sonraki tuşu bekle
        next_char = self._wait_for_key_with_refresh(1.0)
        
        # Timeout oldu (-1) - highlight 1 sn sonra sönecek (check_expired ile)
        if next_char == -1:
            return None
        
        # --- VAO SEQUENCE: ESC + v + a + o ---
        if next_char in (ord('v'), ord('V')):
            self.footer_state.set_vao_progress(2)
            self.renderer.refresh_screen()
            
            second = self._wait_for_key_with_refresh(1.0)
            
            if second == -1:
                return None
            
            if second in (ord('a'), ord('A')):
                self.footer_state.set_vao_progress(3)
                self.renderer.refresh_screen()
                
                third = self._wait_for_key_with_refresh(1.0)
                
                if third == -1:
                    return None
                
                if third in (ord('o'), ord('O')):
                    # VAO tamamlandı!
                    self.footer_state.reset_vao()
                    return "DEV_MESSAGE"
            
            # Sequence tamamlanmadı - sıfırla
            self.footer_state.reset_vao()
            return None
        
        # --- Alt+Arrow ve diğer ESC kombinasyonları ---
        elif next_char == 91:  # '[' - ANSI escape sequence başlangıcı
            self.footer_state.reset_vao()
            self.stdscr.timeout(50)  # Kısa timeout
            try:
                seq_char = self.stdscr.getch()
            except:
                return None

            if seq_char == 49:  # '1' - modifier sequence
                try:
                    self.stdscr.getch()  # ';'
                    mod = self.stdscr.getch()  # modifier (3 = Alt)
                    direction = self.stdscr.getch()  # D=left, C=right
                except:
                    pass
                else:
                    self.stdscr.timeout(100)
                    if mod == 51:  # Alt modifier
                        if direction == 68:  # 'D' - Left
                            return "PREV_TASK"
                        elif direction == 67:  # 'C' - Right
                            return "NEXT_TASK"
            
            elif seq_char == 68:  # Direct Left arrow after ESC[
                self.stdscr.timeout(100)
                return "PREV_TASK"
            elif seq_char == 67:  # Direct Right arrow after ESC[
                self.stdscr.timeout(100)
                return "NEXT_TASK"
            
            self.stdscr.timeout(100)
            return None
        
        elif next_char in (curses.KEY_LEFT, 260):
            # Alt+Left (bazı sistemlerde)
            self.footer_state.reset_vao()
            return "PREV_TASK"
        
        elif next_char in (curses.KEY_RIGHT, 261):
            # Alt+Right (bazı sistemlerde)
            self.footer_state.reset_vao()
            return "NEXT_TASK"
        
        elif next_char == 98:  # 'b' - Mac Option+Left
            self.footer_state.reset_vao()
            return "PREV_TASK"
        
        elif next_char == 102:  # 'f' - Mac Option+Right
            self.footer_state.reset_vao()
            return "NEXT_TASK"
        
        else:
            # Bilinmeyen sequence veya başka tuş - sıfırla
            self.footer_state.reset_vao()
            return None
    
    def _wait_for_key_with_refresh(self, timeout_seconds):
        """Belirtilen süre boyunca tuş bekle, bu sırada ekranı güncellemeye devam et."""
        # Burada redraw optimization gerekmez çünkü ESC sequence çok kısa sürer
        # ve highlight'ın görünmesi için sürekli redraw iyidir.
        self.stdscr.timeout(50)  # 50ms non-blocking
        end_time = time.time() + timeout_seconds
        
        while time.time() < end_time:
            try:
                char = self.stdscr.getch()
            except:
                char = -1
                
            if char != -1:
                self.stdscr.timeout(100)  # Normal timeout'a dön
                return char
            # Ekranı güncelle (highlight görünsün)
            self.renderer.refresh_screen()
        
        self.stdscr.timeout(100)  # Normal timeout'a dön
        return -1  # Timeout

    def _handle_backspace(self):
        self.waiting_for_submit = False
        self.message = ""
        
        if self.cx > 0:
            line = self.buffer[self.cy]
            self.buffer[self.cy] = line[:self.cx-1] + line[self.cx:]
            self.cx -= 1
        elif self.cy > 0:
            current_line = self.buffer.pop(self.cy)
            prev_line_len = len(self.buffer[self.cy-1])
            self.buffer[self.cy-1] += current_line
            self.cy -= 1
            self.cx = prev_line_len

    def _handle_delete(self):
        self.waiting_for_submit = False
        self.message = ""
        
        if self.cx < len(self.buffer[self.cy]):
            line = self.buffer[self.cy]
            self.buffer[self.cy] = line[:self.cx] + line[self.cx+1:]
        elif self.cy < len(self.buffer) - 1:
            next_line = self.buffer.pop(self.cy + 1)
            self.buffer[self.cy] += next_line


def run_editor_session(stdscr, task_info="", hint_text="", initial_code="", 
                       task_status="pending", completed_count=0, skipped_count=0, has_skipped=False):
    """Mevcut curses penceresi içinde editörü çalıştırır (Wrapper olmadan)."""
    editor = Editor(stdscr, task_info=task_info, hint_text=hint_text, 
                   initial_code=initial_code, task_status=task_status,
                   completed_count=completed_count, skipped_count=skipped_count,
                   has_skipped=has_skipped)
    return editor.run()

def run_editor(task_info="", hint_text="", initial_code="", 
               task_status="pending", completed_count=0, skipped_count=0, has_skipped=False):
    """Curses wrapper ile editörü başlatır (Eski uyumluluk için)."""
    return curses.wrapper(lambda stdscr: run_editor_session(stdscr, task_info, hint_text, initial_code, 
                                                            task_status, completed_count, skipped_count, has_skipped))
