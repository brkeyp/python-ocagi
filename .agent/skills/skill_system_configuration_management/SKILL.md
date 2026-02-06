---
name: System Configuration & Dependency Management
description: The master protocol for managing application constants, version enforcement, and external requirements.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
A system built on shaky foundations will collapse. Configuration is the DNA of the runtime environment.

Before modifying constants or startup logic:
1.  **Locate**: Search for `config.py`, `settings.py`, or `main.py`.
2.  **Read**: Read these modules **in their entirety**.
3.  **Catalog**: Understand what is hardcoded and what is dynamic.

**DO NOT PROCEED UNTIL YOU KNOW THE SOURCE OF TRUTH.**

---

# I. The Philosophy of Configuration
Magic numbers are evil. Hardcoded strings are technical debt.
- All constants (Colors, Timeouts, File Names, Messages) must live in a central Config module.
- This allows a single point of change for the entire system behavior.

# II. The Dependency Protocol
The simulator relies on specific environments.
- **Python Version**: We enforce a Minimum Viable Version (e.g., 3.10+).
- **Libraries**: `curses` is non-standard on Windows. We use `windows-curses`.
- **Bootstrapper**: The `main.py` entry point often checks these before importing the rest.

**Key Rule**: If a dependency is missing, we do not crash with a stack trace. We print a helpful, localized error message and exit gracefully.

# III. Protocol for Adding Configuration
When adding a new feature that needs parameters:

1.  **Categorization**:
    - Does it belong in `UI`? `Timing`? `System`?
    - Find the appropriate Class in the Config module.

2.  **Naming Convention**:
    - Use `UPPER_CASE` for constants.
    - Be descriptive (e.g., `ANIMATION_DELAY_MS` is better than `DELAY`).

3.  **Usage**:
    - Import the config module.
    - Reference via `config.Class.CONSTANT`.
    - **NEVER** redefine the value locally.

# IV. Protocol for Version Control
If you must change a core behavior:
1.  **Check Sensitivity**: Does this break save files? (See Data Persistence Skill).
2.  **Check Compatibility**: Does this work on Windows AND macOS? (Use `os.name` checks in Config if needed, but prefer platform-agnostic code).

# V. The Forbidden Actions
- **NEVER** put API keys or secrets in the code (not applicable here, but good practice).
- **NEVER** modify `main.py` logic to bypass dependency checks during production.
- **NEVER** scatter settings across multiple files. Centralize them.

Order is the first law of heaven.
