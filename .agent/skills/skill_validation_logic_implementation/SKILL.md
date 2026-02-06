---
name: Validation Logic Implementation
description: The rigorous protocol for defining truth and partial credit within the simulation's judgment system.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
The creation of validation logic is the creation of Law. A flaw here means a user can be right but told they are wrong, or wrong but told they are right. Both are fatal to the learning experience.

Before writing a single line of logic code:
1.  **Locate**: Search the codebase for the Python module responsible for verification. Look for a file containing functions starting with a standard prefix (e.g., `validate_`) and a dictionary mapping IDs to these functions.
2.  **Read**: Read this module **in its entirety**.
3.  **Pattern Match**: Analyze the signature of existing validator functions. What arguments do they take? What do they return? How do they access the user's variables?

**DO NOT PROCEED UNTIL YOU HAVE MAPPED THE LOGIC.**

---

# I. The Philosophy of Verification
Validation is not Unit Testing.
- **Validation** checks the *User's* code during the simulation. (See this Skill).
- **Unit Testing** checks the *Simulator's* code during development. (See **Internal System Quality Assurance Skill**).

The user is unpredictable. They may solve a problem in infinite ways. Your validator must be **resilient**.
- **Goal**: Check for the *result*, not strict syntax (unless the task requires it).
- **Goal**: Check for side effects (e.g., printed output) if the task implies it.
- **Goal**: Ensure type safety. If the user creates a string instead of an int, tell them.

# II. The Logic Artifact (The Judge)
The system relies on a central Python module to map Task IDs (from the Curriculum) to executable functions.

**The Anatomy of a Validator:**
- **Input 1: Scope**. This is a dictionary representing the sandbox's memory *after* execution. It contains variables like `x`, `y`, `result`.
- **Input 2: Output**. This is a string capturing the `stdout` (print statements) produced by the user's code.
- **Output**: Boolean `True` (Pass) or `False` (Fail).

**Accessing Logic**:
You do not import the user's code. You inspect the `scope` dictionary.
*Example Pattern (Abstract)*:
```python
def validate_X(scope, output):
    # Check if variable exists
    if 'my_var' not in scope: return False
    # Check value
    return scope['my_var'] == 42
```

# III. protocol for Implementation
When adding a new validator for a new Task ID:

1.  **Synchronization**:
    - Ensure you know the exact Integer ID of the task you are implementing. This MUST match the Curriculum ID.

2.  **Creation**:
    - Define a new function in the logic module.
    - Name it consistently with the existing patterns found in the file.

3.  **Registration**:
    - You must add this new function to the **Mapping Dictionary** at the bottom of the file.
    - If you define the function but fail to map it, the Engine will never find it. The task will be impossible to complete.

4.  **Robustness Checks**:
    - What if the user didn't define the variable? (Use `.get()`).
    - What if the user defined it with the wrong type? (Use `isinstance`).
    - What if the user printed the answer instead of saving it? (Check `output` if applicable).

# IV. The Forbidden Actions
- **NEVER** use `eval` or `exec` inside a validator. The code has already run.
- **NEVER** assume a variable exists. Always check existence first.
- **NEVER** change the function signature. The Engine calls it with specific arguments.

Failure to register a validator is a silent system failure. Be vigilant.
