---
name: Internal System Quality Assurance
description: The protocol for maintaining the integrity of the simulator codebase itself through automated testing and rigorous verification.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
The Simulator simulates code. But who simulates the Simulator?
If the engine breaks, the user learns nothing. The watchers must be watched.

Before attempting to modify the test suite:
1.  **Locate**: Search for the directory containing the test definitions (usually `tests/` or `spec/`).
2.  **Read**: Read the Test Configuration file (`conftest.py`) **in its entirety**.
3.  **Trace**: Identify the "Fixtures". How do we fake the Terminal? How do we fake the Filesystem?

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE MOCKING STRATEGY.**

---

# I. The Philosophy of Testing
We distinguish clearly between **Validation** (grading the user) and **Testing** (verifying the app).
- Validation tells the user they are wrong.
- Testing tells the DEVELOPER they are wrong.

**The Test Pyramid**:
- **Unit Tests**: Test the logic of `engine.py` without any UI.
- **Integration Tests**: Test the `controller.py` with a Mock UI.
- **Functional Tests**: Test the `safe_runner.py` with actual subprocesses.

# II. The Mocking Architecture
The Simulator relies heavily on `curses`. `curses` cannot run in a CI/CD environment or a headless test runner.
Therefore, we must **Mock** the display.
- **The Virtual Terminal**: Look for a class that pretends to be `stdscr`. It captures `addstr` calls into a list of strings.
- **The Input Injection**: We do not press physical keys. We push integers into the Input Queue.

# III. Protocol for Adding Tests
When you refactor a core component (e.g., the Tokenizer), you must:

1.  **Isolation**:
    - Create a test file named `test_component_name.py`.
    - Import the component.
    - Do NOT import the full application stack if unnecessary.

2.  **Coverage**:
    - Test the Happy Path (it works).
    - Test the Edge Cases (empty strings, huge numbers).
    - **CRITICAL**: Test the Failure Modes. Does it raise the correct Exception?

3.  **Execution**:
    - Run the tests using the standard runner (e.g., `pytest`).
    - **NEVER** push code that passes "on my machine" but fails the suite.

# IV. The Forbidden Actions
- **NEVER** use `time.sleep()` in tests to wait for a result. Use deterministic synchronization (wait for queue empty, join thread).
- **NEVER** write tests that depend on the physical file system if possible (use `tmp_path` fixture).
- **NEVER** mock too much. If you mock the Engine, the Controller, and the UI, you are testing your mocks, not the code.

Trust is good. Verification is better.
