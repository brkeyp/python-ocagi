# -*- coding: utf-8 -*-
"""
Footer Renderer Modülü
Footer çizimi ve tuş highlight state yönetimi.
"""
import sys
import time
import curses
import config


class FooterState:
    """Footer highlight durumlarını yöneten state class."""
    
    def __init__(self):
        # ESC+VAO sequence progress (0=yok, 1=ESC, 2=ESC+v, 3=ESC+va)
        self.vao_progress = 0
        
        # Toggle state - ipucu açık/kapalı
        self.show_hint = False
        
        # VAO sequence expire timestamp (1 sn sonra sönecek)
        self.vao_expire = 0
    
    def set_vao_progress(self, level):
        """VAO sequence progress ayarla (1 sn sonra sönecek)."""
        self.vao_progress = level
        if level > 0:
            self.vao_expire = time.time() + config.Timing.VAO_EXPIRE_SEC
        else:
            self.vao_expire = 0
    
    def check_expired(self):
        """Expire olan highlight'ları sıfırla. Her refresh'te çağrılmalı."""
        current_time = time.time()
        
        # VAO sequence expire kontrolü (1 sn sonra sönecek)
        if self.vao_expire > 0 and current_time > self.vao_expire:
            self.vao_progress = 0
            self.vao_expire = 0
    
    def reset_vao(self):
        """VAO sequence'ı sıfırla."""
        self.vao_progress = 0
        self.vao_expire = 0


class FooterRenderer:
    """Footer çizim işlemleri."""
    
    def __init__(self, stdscr, footer_state):
        self.stdscr = stdscr
        self.state = footer_state
    
    def draw(self, row, width, editor_state):
        """Footer'ı interaktif renklendirme ile çizer."""
        # Expire kontrolü
        self.state.check_expired()
        
        # 0. Mesaj Kontrolü (Varsa sarı renkte göster ve çık)
        if editor_state.message:
            try:
                self.stdscr.addstr(row, 0, editor_state.message[:width-1], curses.color_pair(config.Colors.YELLOW))
            except curses.error:
                pass
            return

        # Durumları editor_state üzerinden al
        is_buffer_empty = all(line.strip() == "" for line in editor_state.buffer)
        is_locked = editor_state.is_locked
        task_status = editor_state.task_status
        has_skipped = editor_state.has_skipped
        
        col = 0
        
        # Yardımcı fonksiyon: metin çiz ve col güncelle
        def draw_text(text, attr=curses.A_DIM):
            nonlocal col
            if col >= width - 1:
                return
            try:
                display = text[:width - 1 - col]
                self.stdscr.addstr(row, col, display, attr)
                col += len(display)
            except curses.error:
                pass
        
        # Stiller
        HIGHLIGHT = curses.color_pair(config.Colors.GREEN) | curses.A_BOLD  # Yeşil parlak (aktif tuşlar)
        KEY = curses.A_BOLD  # Tuşlar için parlak beyaz
        DIM = curses.A_DIM   # Açıklamalar için soluk
        SEP = " · "          # Modern ayırıcı
        
        # Celebration modunda bazı kısayollar gizlenir
        is_celebration = (task_status == "celebration")
        
        # --- ESC+VAO Mesaj --- (her zaman gösterilir)
        # vao_progress: 0=yok, 1=ESC, 2=ESC+v, 3=ESC+va
        if self.state.vao_progress >= 1:
            draw_text("ESC", HIGHLIGHT)
        else:
            draw_text("ESC", KEY)
        
        if self.state.vao_progress >= 2:
            draw_text("+V", HIGHLIGHT)
        else:
            draw_text("+V", KEY)
        
        if self.state.vao_progress >= 3:
            draw_text("A", HIGHLIGHT)
        else:
            draw_text("A", KEY)
        
        draw_text("O", KEY)
        draw_text(" Mesaj", DIM)
        draw_text(SEP, DIM)
        
        # --- ? İpucu --- (celebration modunda gizle)
        if not is_celebration:
            if self.state.show_hint:
                draw_text("?", HIGHLIGHT)
            else:
                draw_text("?", KEY)
            draw_text(" İpucu", DIM)
            draw_text(SEP, DIM)
        
        # --- Navigasyon --- (her zaman göster)
        if sys.platform == 'darwin':
            draw_text("⌥←/→", KEY)
        else:
            draw_text("Alt+←/→", KEY)
        draw_text(" Soru Geç", DIM)
        draw_text(SEP, DIM)
        
        # --- Sıfırla (sadece boş buffer'da veya kilitli görevde veya celebration'da göster) ---
        if is_buffer_empty or is_locked or is_celebration:
            if sys.platform == 'darwin':
                draw_text("fn+⌫", KEY)
            else:
                draw_text("Del", KEY)
            draw_text(" Sıfırla", DIM)
            draw_text(SEP, DIM)
        
        # --- Çıkış ---
        if sys.platform == 'darwin':
            draw_text("^C", KEY)
        else:
            draw_text("Ctrl+C", KEY)
        draw_text(" Çıkış", DIM)
        
        # --- Görev durumuna göre ek bilgi ---
        if is_celebration:
            # Celebration modunda: sadece atlanmış varsa Enter göster
            if has_skipped:
                draw_text(SEP, DIM)
                draw_text("Enter", KEY)
                draw_text(" Atlanmış İlk Soruya Git", DIM)
            # has_skipped=False ise Enter gösterilmez
        elif task_status == "skipped":
            draw_text(SEP, DIM)
            draw_text("ÇiftEnter", KEY)
            if is_buffer_empty:
                draw_text(" Cevabı Tekrar Gör", DIM)
            else:
                draw_text(" Gönder", DIM)
        elif task_status == "pending":
            draw_text(SEP, DIM)
            draw_text("ÇiftEnter", KEY)
            if is_buffer_empty:
                draw_text(" Soruyu Atla", DIM)
            else:
                draw_text(" Gönder", DIM)
