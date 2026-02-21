# -*- coding: utf-8 -*-
"""
Python Ocağı - Ana UI Modülü
Curses tabanlı kod editörü.
"""
import sys
import os
import time
import curses
import locale
import config
import threading

# Locale ayarı - Türkçe karakter desteği için
try:
    locale.setlocale(locale.LC_ALL, '')
except Exception:
    pass  # Locale setting may fail on some systems - non-critical

# ESCDELAY ayarı - ESC tuşunun anında tepki vermesi için
# (curses varsayılan olarak escape sequence bekler, bu gecikmeye neden olur)
os.environ.setdefault('ESCDELAY', config.Timing.ESCDELAY_ENV)

# Alt modüllerden import
from ui.utils import OSUtils
from ui.footer import FooterState
from ui.renderer import EditorRenderer
from ui.colors import init_colors
from input.api import EventType, InputEvent
from input.curses_driver import CursesInputDriver


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
            curses.set_escdelay(int(config.Timing.ESCDELAY_ENV))  # Python 3.9+
        except AttributeError:
            pass  # Eski Python sürümlerinde env variable kullanılır
        
        # Renk çiftleri (merkezi modülden)
        init_colors()


        
        # Thread Protection
        self.lock = threading.Lock()
        
        # Input Driver
        # Pass the lock to ensure input thread and main thread don't collision on stdscr
        self.driver = CursesInputDriver(stdscr, lock=self.lock)
        self.vao_step = 0



    def run(self):
        """Editörü başlatır ve kodu döndürür."""
        should_redraw = True
        
        while True:
            # 1. Timer Logic (Message & VAO)
            current_time = time.time()
            
            # Message Autoclear
            if self.message and self.message_timestamp:
                if current_time - self.message_timestamp > config.Timing.MSG_AUTOCLEAR_SEC:
                    self.message = ""
                    self.message_timestamp = None
                    should_redraw = True

            # VAO Expiration
            if self.footer_state.vao_expire > 0:
                 self.footer_state.check_expired()
                 if self.footer_state.vao_progress == 0:
                     self.vao_step = 0
                     should_redraw = True
            
            # 2. Draw
            if should_redraw:
                with self.lock:
                    self.renderer.refresh_screen()
                should_redraw = False
                
            # 3. Input Timeout / Animations Update
            has_active_timer = (self.message is not None and self.message != "") or \
                               (self.footer_state.vao_progress > 0)
            
            # Fixed 30 FPS update rate (approx 33ms) to allow background tasks/animations
            timeout = 33
            
            # 4. Get Event
            event = self.driver.get_event(timeout)
            
            if event.type == EventType.TIMEOUT:
                continue
                
            should_redraw = True # Input received
            
            # --- VAO LOGIC ---
            if self.vao_step > 0:
                expected = None
                if self.vao_step == 1: expected = 'v'
                elif self.vao_step == 2: expected = 'a'
                elif self.vao_step == 3: expected = 'o'
                
                if event.type == EventType.CHAR and event.value and event.value.lower() == expected:
                     if expected == 'o':
                         self.footer_state.reset_vao()
                         self.vao_step = 0
                         return "DEV_MESSAGE"
                     else:
                         self.vao_step += 1
                         self.footer_state.set_vao_progress(self.vao_step)
                         continue
                elif event.type != EventType.TIMEOUT:
                    # Broken sequence
                    self.footer_state.reset_vao()
                    self.vao_step = 0
                    # Fallthrough
            
            # Start VAO on ESCAPE
            if event.type == EventType.ESCAPE:
                self.message = ""
                self.footer_state.set_vao_progress(1) # Highlight 1
                self.vao_step = 1
                should_redraw = True
                continue
                
            # --- EVENT HANDLING ---
            if event.type == EventType.EXIT:
                raise KeyboardInterrupt
                
            elif event.type == EventType.PREV_TASK:
                self.footer_state.reset_vao()
                return "PREV_TASK"
                
            elif event.type == EventType.NEXT_TASK:
                 self.footer_state.reset_vao()
                 return "NEXT_TASK"

            elif event.type == EventType.RESIZE:
                 # Curses should have updated lines/cols by now if handled in driver
                 should_redraw = True
                 continue

            elif event.type == EventType.SHOW_HINT:
                 self.footer_state.show_hint = not self.footer_state.show_hint
                 continue

            # --- NAVIGATION ---
            elif event.type == EventType.UP:
                if self.cy > 0:
                    self.cy -= 1
                    self.cx = min(self.cx, len(self.buffer[self.cy]))
                self.waiting_for_submit = False
                self.message = ""

            elif event.type == EventType.DOWN:
                if self.cy < len(self.buffer) - 1:
                    self.cy += 1
                    self.cx = min(self.cx, len(self.buffer[self.cy]))
                self.waiting_for_submit = False
                self.message = ""

            elif event.type == EventType.LEFT:
                if self.cx > 0:
                    self.cx -= 1
                elif self.cy > 0:
                    self.cy -= 1
                    self.cx = len(self.buffer[self.cy])
                self.waiting_for_submit = False
                self.message = ""

            elif event.type == EventType.RIGHT:
                if self.cx < len(self.buffer[self.cy]):
                    self.cx += 1
                elif self.cy < len(self.buffer) - 1:
                    self.cy += 1
                    self.cx = 0
                self.waiting_for_submit = False
                self.message = ""

            # --- EDITING ---
            elif event.type == EventType.BACKSPACE:
                if self.is_locked:
                    self.message = config.UI.MSG_TASK_COMPLETED
                    self.message_timestamp = time.time()
                else:
                    self._handle_backspace()

            elif event.type == EventType.DELETE:
                if self.is_locked:
                    self.message = config.UI.MSG_TASK_COMPLETED
                    self.message_timestamp = time.time()
                else:
                    self._handle_delete()

            elif event.type == EventType.RESET_ALL:
                if self.is_locked:
                    self.message = config.UI.MSG_TASK_COMPLETED
                    self.message_timestamp = time.time()
                else:
                    self.message = config.UI.MSG_RESET_CONFIRM
                    self.renderer.refresh_screen()
                    while True:
                        conf_event = self.driver.get_event(config.Timing.TIMEOUT_BLOCKING)
                        if conf_event.type == EventType.CHAR and conf_event.value and conf_event.value.lower() == 'e':
                            return "RESET_ALL"
                        elif conf_event.type in (EventType.CHAR, EventType.ESCAPE, EventType.ENTER, EventType.UP, EventType.DOWN, EventType.LEFT, EventType.RIGHT):
                            self.message = ""
                            should_redraw = True
                            break

            # --- ENTER ---
            elif event.type == EventType.ENTER:
                if self.task_status == "celebration":
                    if self.has_skipped:
                        return "GOTO_FIRST_SKIPPED"
                    continue
                elif self.is_locked:
                    self.message = config.UI.MSG_TASK_COMPLETED
                    self.message_timestamp = time.time()
                elif self.task_status == "skipped":
                    if self.waiting_for_submit:
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        if is_buffer_empty:
                            return None 
                        else:
                            return "\n".join(self.buffer)
                    else:
                        self._handle_newline()
                else: # pending
                    if self.waiting_for_submit:
                        is_buffer_empty = all(line.strip() == "" for line in self.buffer)
                        if is_buffer_empty:
                            return None 
                        else:
                            return "\n".join(self.buffer)
                    else:
                        self._handle_newline()

            # --- CHAR INPUT ---
            elif event.type == EventType.CHAR:
                if self.is_locked:
                    self.message = config.UI.MSG_TASK_COMPLETED
                    self.message_timestamp = time.time()
                    continue
                
                self.waiting_for_submit = False
                self.message = ""
                
                line = self.buffer[self.cy]
                self.buffer[self.cy] = line[:self.cx] + event.value + line[self.cx:]
                self.cx += 1



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

    def _handle_newline(self):
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
            if self.task_status == "skipped":
                 self.message = config.UI.MSG_PRESS_ENTER_AGAIN # Corrected for Skipped
            else:
                 self.message = config.UI.MSG_SKIP_OR_TYPE
        else:
            self.message = config.UI.MSG_SUBMIT_OR_TYPE


def run_editor_session(stdscr, task_info="", hint_text="", initial_code="", 
                       task_status="pending", completed_count=0, skipped_count=0, has_skipped=False):
    """Mevcut curses penceresi içinde editörü çalıştırır (Wrapper olmadan)."""
    editor = Editor(stdscr, task_info=task_info, hint_text=hint_text, 
                   initial_code=initial_code, task_status=task_status,
                   completed_count=completed_count, skipped_count=skipped_count,
                   has_skipped=has_skipped)
    try:
        return editor.run()
    finally:
        editor.driver.close()

def run_editor(task_info="", hint_text="", initial_code="", 
               task_status="pending", completed_count=0, skipped_count=0, has_skipped=False):
    """Curses wrapper ile editörü başlatır (Eski uyumluluk için)."""
    return curses.wrapper(lambda stdscr: run_editor_session(stdscr, task_info, hint_text, initial_code, 
                                                            task_status, completed_count, skipped_count, has_skipped))
