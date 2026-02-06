---
name: Application State Management
description: The protocol for governing the central simulation lifecycle, state transitions, and high-level decision making.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
The Engine is the brain. It does not see, it does not hear; it *knows*. It maintains the truth of the world.

Before attempting to modify the core logic:
1.  **Locate**: Search for the "Engine" or "Simulation" class. This is the central hub.
2.  **Read**: Read this module **in its entirety**.
3.  **Trace**: Follow the data flow. How does `Input` -> `Engine` -> `Action` -> `Ui` work?

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE ACTION-BASED ARCHITECTURE.**

---

# I. The Philosophy of State
The Engine is a State Machine.
- At any moment, the user is in a specific state (e.g., `PENDING` a task, `COMPLETED` a task, `CELEBRATING` victory).
- The Engine's job is to calculate the **Next Action** based on the current state and the user's input.
- It should be "Pure" logic where possible. It takes inputs and returns Action objects. It should not draw to `stdscr` directly.

# II. The Action Protocol
The Engine usually communicates with the UI via "Action Data Classes".
- **ActionRenderEditor**: "Please draw the editor with this text."
- **ActionShowMessage**: "Please show this pop-up."
- **ActionExit**: "Please kill the program."

**Why this matters**:
This separation allows us to test the logic without a terminal. If you break this separation (e.g., adding `print()` inside the Engine), you break the architecture.

# III. Helper Functions
The state is complex. It involves:
- Current Step ID.
- Completed Tasks list.
- Skipped Tasks list.
- User Code history.

**Protocol for State Modification**:
- **NEVER** modify the state dictionary manually/randomly. Use the provided helper functions (e.g., `mark_task_completed`).
- These helpers ensure that side effects (like saving to disk) happen automatically.

# IV. Protocol for Logic expansion
When adding a new feature (e.g., a "Hint" system):

1.  **Define the Action**:
    - Create a new Action Data Class if the UI needs to do something new (e.g., `ActionShowHint`).

2.  **Handle the Input**:
    - In the `process_input` method, detect the command (e.g., `SHOW_HINT`).

3.  **Update the State**:
    - If needed, record that the hint was shown (maybe deduct points?).

4.  **Return the Action**:
    - Return the new Action object so the Controller can execute it.

# V. The Forbidden Actions
- **NEVER** import `curses` or `ui` inside the Engine (circular dependency risk).
- **NEVER** perform blocking I/O (like `time.sleep`) inside the logic calculation, unless it's part of a specific "Wait" action instruction.
- **NEVER** hardcode Task IDs in the logic logic (e.g., `if id == 10: do_special_thing`). Use flags in the curriculum data instead.

Think clearly. The Engine must not falter.
