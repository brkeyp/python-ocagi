import time
import sys
import curses
import engine
import config
from ui.editor import run_editor_session
from ui.utils import OSUtils, suspend_curses

def handle_action(stdscr, action):
    """Executes non-render actions (Messages, Custom Views, Exit)."""
    if not action:
        return

    if isinstance(action, engine.ActionShowMessage):
        with suspend_curses(stdscr):
            if action.clear_screen:
                OSUtils.clear_screen()
            
            # Print Title
            if action.type == 'error':
                 print(f"\n{action.title}")
            elif action.title:
                 print(f"\n{action.title}")
            
            if action.type != 'reset' and action.title: # Reset has its own format in content usually or we standardise
                 # Original code had different formats.
                 # Success: Check mark title.
                 # Error: X mark title.
                 pass

            # Print Content
            if action.content:
                if action.type in ['solution', 'error', 'info']:
                     print("-" * 30)
                     print(action.content)
                     print("-" * 30)
                else:
                     # Success / Reset
                     print(action.content)
            
            # Interactions
            if action.wait_for_enter:
                if action.type == 'error':
                    input(f"\n{config.UI.PROMPT_RETRY}")
                else:
                    input(f"\n{config.UI.PROMPT_CONTINUE}")
            else:
                time.sleep(config.Timing.ACTION_WAIT_SUCCESS if action.type == 'success' else config.Timing.ACTION_WAIT_DEFAULT)
                
    elif isinstance(action, engine.ActionCustomView):
        if action.view_name == "dev_message":
            with suspend_curses(stdscr):
                 try:
                     from ui.dev_message import show_developer_message
                     show_developer_message(stdscr)
                 except Exception:
                     pass

    elif isinstance(action, engine.ActionExit):
        raise KeyboardInterrupt

def validate_terminal_size():
    """Terminal boyutunun en az 20x10 olduğunu kontrol eder."""
    try:
        import shutil
        cols, lines = shutil.get_terminal_size(fallback=(80, 24))
        
        if cols < config.Layout.MIN_WIDTH or lines < config.Layout.MIN_HEIGHT:
            print(f"\n❌ TERMINAL BOYUTU ÇOK KÜÇÜK ({cols}x{lines})")
            print("Lütfen pencereyi genişletin ve uygulamayı yeniden başlatın.")
            print(f"Minimum gerekli boyut: {config.Layout.MIN_WIDTH}x{config.Layout.MIN_HEIGHT}")
            input(f"\n{config.UI.PROMPT_EXIT}")
            return False
        return True
    except Exception:
        return True

def run_loop(stdscr):
    # Initial setup
    curses.curs_set(1)
    
    simulation = engine.SimulationEngine()
    
    while True:
        # Determine what to show on main UI
        action = simulation.get_next_action()
        
        if isinstance(action, engine.ActionExit):
            raise KeyboardInterrupt
            
        elif isinstance(action, engine.ActionRenderEditor):
             user_code = run_editor_session(
                stdscr,
                task_info=action.task_info,
                hint_text=action.hint_text,
                initial_code=action.initial_code,
                task_status=action.task_status,
                completed_count=action.completed_count,
                skipped_count=action.skipped_count
             )
             # Process input (Code or Command)
             result_action = simulation.process_input(user_code)
             handle_action(stdscr, result_action)

        elif isinstance(action, engine.ActionRenderCelebration):
             user_code = run_editor_session(
                stdscr,
                task_info="",
                hint_text="",
                initial_code="",
                task_status="celebration",
                completed_count=action.completed_count,
                skipped_count=action.skipped_count,
                has_skipped=action.has_skipped
             )
             result_action = simulation.process_input(user_code)
             handle_action(stdscr, result_action)

def check_exit_key():
    import os, sys
    if os.name == 'nt':
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b'\r', b'\n'):
                return True
        return False
    else:
        import select
        i, _, _ = select.select([sys.stdin], [], [], 0.0)
        if i:
            try:
                char = sys.stdin.read(1)
                if char in ('\r', '\n'):
                    return True
            except Exception:
                pass
        return False

def run_controller():
    # Terminal check
    if not validate_terminal_size():
        return

    # macOS spawn fix
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

    try:
        curses.wrapper(run_loop)
    except curses.error as e:
        OSUtils.clear_screen()
        print("\n❌ TERMİNAL BAŞLATMA HATASI (curses.error)")
        print("-" * 40)
        print(f"Hata Detayı: {e}")
        print("\nOlası Çözümler:")
        print("1. 'TERM' ortam değişkenini kontrol edin (örn: xterm-256color).")
        print("2. Windows kullanıyorsanız 'windows-curses' düzgün yüklenmemiş olabilir.")
        print("-" * 40)
        input(f"\n{config.UI.PROMPT_EXIT}")
        sys.exit(1)
    except KeyboardInterrupt:
        # Ctrl+C Clean exit
        OSUtils.clear_screen()
        
        # ANSI Renk Kodları
        turquoise = "\033[38;2;64;224;208m"
        reset = "\033[0m"
        dark_gray = "\033[90m"
        
        print(f"\n{turquoise}{config.UI.MSG_EXIT}{reset}\n\n")
        
        # Geri sayım ve Enter tetikleyicisi
        for i in range(10, 0, -1):
            sys.stdout.write(f"\r\033[K{dark_gray}Terminal {i:02d} saniye içinde kapanacaktır...{reset}\n")
            sys.stdout.write(f"\033[K{dark_gray}Hemen çıkmak için ENTER'a basın.{reset}")
            sys.stdout.flush()
            
            interrupted = False
            for _ in range(10):  # 1 saniyelik bekleyişi 0.1s'lik parçalarda kontrol et
                if check_exit_key():
                    interrupted = True
                    break
                time.sleep(0.1)
                
            if interrupted or i == 1:
                break
                
            # Cursor'u 1 satır yukarı al ve satır başına çek
            sys.stdout.write("\033[A\r")
            
        print("\n\n")
        sys.exit(130)
    except Exception as e:
        OSUtils.clear_screen()
        print("\n❌ BEKLENMEYEN UYGULAMA HATASI")
        print("-" * 40)
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        print("-" * 40)
        input(f"\n{config.UI.PROMPT_EXIT}")
        sys.exit(1)
