---
name: Secure Execution Environment Governance
description: The protocol for operating the isolated sandbox, managing process lifecycles, and enforcing strict resource limits on user code.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
The Sandbox is the prison that holds chaos at bay. The user's code is untrusted. If it escapes, it destroys the system.

Before touching the execution logic:
1.  **Locate**: Search for "Sandbox", "Runner", or "Guardian" modules.
2.  **Read**: Read them **in their entirety**.
3.  **Audit**: Identify the Isolation Mechanism (Is it `exec`? `subprocess`? `multiprocessing`?).

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE SECURITY BOUNDARY.**

---

# I. The Philosophy of Containment
We do not run user code in the main process.
- **Why?** One infinite loop (`while True: pass`) freezes the UI.
- **Why?** One `sys.exit()` kills the simulator.
- **Why?** One `import os; os.remove('main.py')` destroys the project.

We must rely on **Process Isolation** and **Capabilities Reduction**.

# II. The Security Architecture
The system likely uses a multi-layered approach:

1.  **The Process Layer**:
    - User code runs in a separate Process (via `multiprocessing`).
    - This allows us to kill it if it times out.

2.  **The Scope Layer**:
    - We provide a custom `globals` dictionary.
    - We do NOT provide the real `builtins`. We provide a sanitized version.

3.  **The Import Layer**:
    - We overwrite `__import__`.
    - We whitelist only safe modules (`math`, `random`, `datetime`).
    - Anything else raises a Security Exception.

# III. Protocol for Modifying the Sandbox
When you need to allow a new module (e.g., `collections`):

1.  **Assess Risk**:
    - Does this module allow file access? (No).
    - Does it allow network access? (No).
    - Does it allow memory exhaustion? (Maybe).

2.  **Implementation**:
    - Locate the `ALLOWED_MODULES` set.
    - Add the module name.
    - **CRITICAL**: Verify that the custom importer logic actually checks this set.

3.  **Resource Limits**:
    - If you are touching the Runner, ensure Timeouts are enforced (`process.join(timeout)`).
    - Ensure Memory limits (if implemented via `resource` module) are set.

# IV. The Forbidden Actions
- **NEVER** expose `os`, `sys`, `subprocess` to the user scope.
- **NEVER** run user code in the Main UI Thread.
- **NEVER** rely solely on string finding (regex) to block malice. You must block it at the runtime/scope level.

Security is not a feature; it is the environment.
