---
name: Curriculum Architecture & Design
description: A comprehensive protocol for designing, structuring, and implementing educational content within the simulation.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
Before taking *any* action to modify, extend, or analyze the curriculum, you satisfy the following condition without exception:

1.  **Tabula Rasa**: You must assume you know nothing about the file structure.
2.  **Locate**: You must use file system tools to locate the primary data artifact containing the lesson definitions (Standard format is JSON).
3.  **Ingest**: You must read this file **in its entirety**.
4.  **Schema Internalization**: You must parse the structure of an individual lesson entry until you understand the exact relationship between the Identifier, the Category, the Task Description, the Solution, and the Hint.

**DO NOT PROCEED UNTIL YOU HAVE READ THE LIVE DATA.**

---

# I. The Philosophy of Curriculum
The Curriculum is not merely a list of questions; it is the *narrative arc* of the user's journey. Each entry is a stepping stone. A gap in the stones results in a user falling into the abyss of confusion.

To design a curriculum item is to act as both Architect and Teacher. You must predict the user's mental model and challenge it precisely enough to induce learning, but not so much as to induce panic.

# II. The Data Structure (The DNA)
The simulation relies on a strict, serialized data format. You must identify the file that holds this data. It is never to be referenced by name in your thoughts, but found by its signature.

**The Signature Traits:**
- It is a JSON Array.
- It contains Objects representing "Tasks".
- Each Task has a unique Integer Identifier.
- Each Task belongs to a specific Category string.
- Each Task has a `task` field containing the prompt shown to the user.
- Each Task has a `sol` field containing the canonical solution code.
- Each Task has a `hint` field.

**Critical Rule of Uniqueness:**
The Integer Identifier acts as the primary key for the entire system. It links the static data to the dynamic validation logic. **YOU MUST NEVER DUPLICATE AN ID.** Before adding a task, you must scan the entire existing array to find the highest ID and increment it.

# III. The Formatting Standard
The `task` field is the user's window into the challenge. Visual hierarchy is paramount.
- You must inspect existing entries to match the style exactly.
- Typically, the format includes a Numbered Title followed by a Newline, followed by the instruction.
- Observe how `\n` characters are used to control spacing.
- Observe the tone of the instructions. Are they imperative? Descriptive? playful? Match it.

# IV. Protocol for Expansion
When you are tasked with adding new content:

1.  **Discovery Phase**:
    - List the directory contents.
    - Identify the JSON data file.
    - Read the JSON data file.
    - Identify the current "Highest ID".

2.  **Design Phase**:
    - Draft your new tasks mentally.
    - Ensure they fit the category structure found in the file.
    - Ensure the difficulty curve is smooth relative to the previous tasks.

3.  **Implementation Phase**:
    - Construct the JSON object.
    - Insert it into the array (preserving order is preferred but ID is critical).
    - **CRITICAL**: You are not done. Data is useless without Verification. You must immediately reference the **Validation Logic Implementation** skill to create the corresponding check. Data and Logic must be twins; one cannot exist without the other.

4.  **Verification Phase**:
    - Verify that your JSON is valid.
    - Verify that no trailing commas or syntax errors exist that would crash the loader.

# V. The Forbidden Actions
- **NEVER** guess the next ID. Count.
- **NEVER** modify an existing ID (this breaks user save files).
- **NEVER** place the Solution code in the Hint field.

Proceed with the gravity this task deserves.
