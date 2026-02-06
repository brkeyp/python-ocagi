---
name: User Input Event Handling
description: The protocol for intercepting, interpreting, and routing user signals (keyboard events) within the simulation.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
Input is the lifeline of interaction. If the system fails to catch a keypress, the user feels ignored. If it misinterprets a signal, the user feels betrayed.

Before modifying control flow:
1.  **Locate**: Search for the "Input Driver" or "Controller" modules. Identify where `getch()` or event queues are managed.
2.  **Read**: Read these modules **in their entirety**.
3.  **Map**: Create a mental map of Raw Keycodes -> Abstract Events (e.g., Key `10` -> `EVENT_ENTER`).

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE EVENT LOOP.**

---

# I. The Philosophy of Interaction
Input handling must be **Deterministic** and **Responsive**.
- **Deterministic**: Pressing 'A' should always do the same thing in the same context.
- **Responsive**: The loop must check for input frequently enough that the user perceives zero latency.

# II. The Input Architecture
The system likely uses a driver-pattern to abstract raw `curses` keys.

**Component identification:**
- **The Polling Loop**: Look for a `while` loop that calls `driver.get_event()`.
- **The Timeout**: Input is often non-blocking code with a timeout (e.g., 33ms/50ms). This allows the UI to animate while waiting for keys.
- **The Event Enum**: Look for a class defining types like `EXIT`, `SUBMIT`, `UP`, `DOWN`.

---

# III. Thread Safety & Locking (CRITICAL)
If the input runs in a separate thread (e.g., `input_threaded.py`):
- **The Danger**: `curses` is NOT thread-safe. You cannot call `getch()` while another thread calls `refresh()`.
- **The Protocol**: usage of `threading.Lock()` is MANDATORY.
    - Acquire the lock before calling `stdscr` methods.
    - Release the lock immediately after.
    - **NEVER** hold the lock during a `time.sleep()`.

---

# IV. Handling Special Keys
Terminals are ancient technology. Keycodes vary by OS.
- **Enter Key**: Can be `10`, `13`, or even `343` (Numpad).
- **Backspace**: Can be `8`, `127`, `263`, or `330`.
- **Esc Delay**: The Esc key (`27`) is notoriously slow in raw curses due to escape sequence ambiguity. Modern systems use specific env vars to fix this.

# V. Protocol for Adding Controls
When you need to add a new hotkey or command:

1.  **Registration**:
    - Add the new Event Type to the Event Enum.
    - Map the physical keycode(s) to this Event Type in the Input Driver.

2.  **Handling**:
    - Go to the Controller or Editor logic.
    - Add a case for the new Event Type.
    - **CRITICAL**: Ensure the action starts and finishes within one frame budget (~30ms) or runs asynchronously, to avoid freezing the UI.

3.  **Feedback**:
    - Every action should have a visual reaction. If the user presses "Save", show a "Saved" message.

# VI. The Forbidden Actions
- **NEVER** use `input()` (blocking standard input). It pauses the entire world.
- **NEVER** ignore `KeyboardInterrupt` (Ctrl+C) completely; handle it gracefully to clean up the terminal state.
- **NEVER** hardcode magic numbers for keys in the logic layer. Use the mapped constants.

Listen carefully. The user is speaking.
