---
name: Visual Interface Engineering
description: The master protocol for manipulating the terminal display, handling render loops, and ensuring visual stability.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
The Visual Interface is the only reality the user perceives. A flicker, a misalignment, or a color error breaks the illusion of solidity.

Before attempting to modify the screen output:
1.  **Locate**: Search for the Python modules responsible for managing the `curses` library interface. Look for "Renderer" classes.
2.  **Read**: Read these modules **in their entirety**.
3.  **Trace**: Understand the "Draw Loop". Identify the sequence: Erase -> Construct Buffer -> Add Strings -> Refresh.

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE COORDINATE SYSTEM.**

---

# I. The Philosophy of the Console
We do not have pixels; we have cells. We do not have transparency; we have background colors.
The philosophy of this simulation's UI is **Stability**.
- The screen should not scroll unexpectedly.
- The cursor must be exactly where the user expects it.
- Text must wrap intelligently, not brutally.

# II. The Rendering Architecture
The system typically abstracts `curses` calls into a specialized Class.

**Key Concepts to Identify in the Code:**
- **The Screen Object (`stdscr`)**: The root window.
- **Color Pairs**: Curses handles colors as foreground/background pairs. You must identify where these ints are defined (often in a Config module).
- **The Refresh Cycle**: calling `refresh()` is expensive. Look for `noutrefresh()` and `doupdate()` patterns which are used for performance double-buffering.

# III. Coordinate Systems (Y, X)
**CRITICAL**: `curses` uses `(y, x)` addressing (Row, Column), NOT `(x, y)`.
- `0, 0` is the top-left corner.
- `HEIGHT, WIDTH` are the boundaries. Writing to the absolute bottom-right corner often causes an error/scroll. Avoid it.

---

# IV. Protocol for UI Modification
When you need to add a new visual element (e.g., a status bar, a popup):

1.  **Dimension Analysis**:
    - Calculate the available space. check `config.Layout` constants if available.
    - Handle window resizing events. What happens if the terminal mimics a mobile screen?

2.  **Palette Selection**:
    - Use only existing color pair constants. Do not hardcode integers (like `1` or `2`). Use the named constants (e.g., `Colors.RED`).
    - **Syntax Highlighting**: If drawing code, do not parse it here. Use the **Static Code Analysis Skill** to get tokens, then map tokens to colors here.

3.  **Drawing Logic Implementation**:
    - Use `try/except` blocks around `addstr` calls. Writing outside bounds raises `curses.error`. We must catch this to prevent crashes.
    - Always prioritize the "Header" and "Footer" as functional anchors.

**Protocol for Modal Overlays (e.g., DevScreen)**:
- If a screen takes over the main loop (e.g., `DeveloperMessageScreen`), it effectively pauses the Engine.
- Ensure it handles its own input loop and `stdscr.clear()` on exit to restore the main UI cleanly.

---

# V. The Forbidden Actions
- **NEVER** use `print()` in the UI module. It ruins the curses buffer layout.
- **NEVER** assume a fixed terminal size (e.g., 80x24). Always query `getmaxyx()`.
- **NEVER** change the cursor visibility (`curs_set`) without resetting it.

The screen is a stage. Keep it clean.
