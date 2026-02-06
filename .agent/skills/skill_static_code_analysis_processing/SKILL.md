---
name: Static Code Analysis & Processing
description: The protocol for parsing, analyzing, and transforming Python source code texts within the editor context.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
Code is not a string. Code is a Tree. Code is a Stream of Tokens.
To render code, we must understand it. To validate code, we sometimes must dissect it.

Before modifying the Tokenizer or Parsing logic:
1.  **Locate**: Search for the "Tokenizer" or "Lexer" module.
2.  **Read**: Read this module **in its entirety**.
3.  **Map**: Understand the State Machine. How does it transition from `ROOT` to `STRING` to `COMMENT`?

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE TOKEN TYPES.**

---

# I. The Philosophy of Syntax
We are building a Python course. We cannot fail to parse Python.
- If the user types `def foo():`, we must see `KEYWORD` -> `TEXT` -> `OP`.
- If we color `def` as a Variable, we confuse the user.
- If we fail to handle `'''multi-line strings'''`, we look amateur.

# II. The State Machine Architecture
Parsing is often implemented as a finite state machine (FSM).
- **State**: Where are we? (Inside a string? Inside a comment? At the start of a line?)
- **Transition**: When we see a character, do we change state?
- **Token**: The chunk of text we just finished processing.

**Key Challenges**:
- **Escaping**: `\"` inside a string does NOT end the string.
- **Triple Quotes**: They consume newlines.
- **Comments**: They consume everything until the newline.

# III. Protocol for Extension
When you need to add support for a new syntax element (e.g., F-Strings, or Python 3.12 syntax):

1.  **Identify the Marker**:
    - What character triggers the new state? (e.g., `f"`).

2.  **Update the Enum**:
    - Add a new `TokenType` if needed.

3.  **Update the Loop**:
    - In the main `tokenize` loop, add a condition for the marker.
    - Ensure it doesn't conflict with existing logic (e.g., check `f` isn't just a variable name).

4.  **Verify**:
    - Use the Internal QA Skill. Add a test case with the new syntax.
    - Ensure it produces the expected list of tokens.

# IV. The Forbidden Actions
- **NEVER** use `eval()` to check syntax. It executes code. Dangerous.
- **NEVER** use simple `split(' ')`. Code has spaces inside strings.
- **NEVER** rely on rigid regex for nested structures (like parentheses). A state machine is safer.

See the structure beneath the text.
