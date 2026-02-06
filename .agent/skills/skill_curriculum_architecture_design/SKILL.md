---
name: Curriculum Architecture & Design
description: A comprehensive protocol for designing, structuring, and implementing educational content within the simulation.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
Before taking *any* action to modify, extend, or analyze the curriculum, you satisfy the following condition without exception:

1.  **Tabula Rasa**: You must assume you know nothing about the file structure.
2.  **Locate**: You must use file system tools to locate the `curriculum/manifest.json` and scan chapter directories.
3.  **Ingest**: You must read the manifest and sample `task.json` files to understand the current structure.
4.  **Schema Internalization**: You must parse the structure of an individual lesson entry until you understand the exact relationship between the UUID, the Category, the Task Description, the Solution, and the Hint.

**DO NOT PROCEED UNTIL YOU HAVE READ THE LIVE DATA.**

---

# I. The Philosophy of Curriculum
The Curriculum is not merely a list of questions; it is the *narrative arc* of the user's journey. Each entry is a stepping stone. A gap in the stones results in a user falling into the abyss of confusion.

To design a curriculum item is to act as both Architect and Teacher. You must predict the user's mental model and challenge it precisely enough to induce learning, but not so much as to induce panic.

# II. The Data Structure (The DNA)

## 2.1 Directory-Based Architecture (Current Standard)
The simulation uses a **hierarchical directory structure**:

```
curriculum/
├── manifest.json           # Chapter ordering
├── 01_temeller/            # Chapter folder
│   ├── 001_merhaba_python/ # Lesson folder
│   │   ├── task.json       # Lesson definition
│   │   ├── validation.py   # Validation logic
│   │   └── solution.py     # Canonical solution
│   └── 002_next_lesson/
└── 02_stringler/
```

## 2.2 The Manifest (manifest.json)
Defines chapter order and metadata:
```json
{
  "chapters": [
    {"slug": "01_temeller", "title": "Temeller"},
    {"slug": "02_stringler", "title": "Stringler"}
  ]
}
```

## 2.3 The Lesson Definition (task.json)
Each lesson folder contains a `task.json` with this schema:
```json
{
  "id": "001_lesson_slug",        // Folder-based ID
  "uuid": "xxxxxxxx-xxxx-...",    // STABLE PRIMARY KEY (UUID v4)
  "category": "Chapter Name",     // Display category
  "title": "Lesson Title",
  "description": "User-facing task description",
  "hint": "Helpful hint without revealing answer",
  "type": "code",                 // Task type
  "xp": 10,                       // Experience points
  "tags": ["tag1", "tag2"]        // Searchable tags
}
```

**Critical Rule of Uniqueness:**
The **UUID** is the immutable primary key. It links user progress to lessons.
- **NEVER** change an existing UUID (this breaks user save files).
- **ALWAYS** generate new UUIDs with `uuid.uuid4()` for new lessons.

## 2.4 Lesson Folder Naming Convention
```
NNN_descriptive_slug/
│
├── NNN = Zero-padded sequential number (001, 002, ...)
└── descriptive_slug = Lowercase, underscores, ASCII-safe
```

# III. The Formatting Standard
The `description` field is the user's window into the challenge. Visual hierarchy is paramount.
- Inspect existing entries to match the style exactly.
- Use clear, imperative Turkish instructions.
- Include variable names in single quotes: `'degisken'`
- Observe the tone: educational, encouraging, precise.

# IV. Protocol for Expansion
When tasked with adding new content:

## 4.1 Discovery Phase
1. List `curriculum/` directory contents.
2. Read `manifest.json` for chapter structure.
3. Scan target chapter folder for existing lessons.
4. Identify the highest lesson number (e.g., `003_` means next is `004_`).

## 4.2 Design Phase
1. Draft your new tasks mentally.
2. Ensure they fit the category structure.
3. Ensure the difficulty curve is smooth relative to previous tasks.

## 4.3 Implementation Phase
1. Create the lesson directory: `NNN_lesson_slug/`
2. Generate a new UUID: `python3 -c "import uuid; print(uuid.uuid4())"`
3. Create `task.json` with full schema.
4. Create `validation.py` with `validate(scope, output)` function.
5. Create `solution.py` with the canonical answer.
6. **CRITICAL**: Reference the **Validation Logic Implementation** skill for validation patterns.

## 4.4 Verification Phase
1. Run `CurriculumManager.load()` to verify parsing.
2. Test the lesson in the simulator.
3. Verify solution passes validation.

# V. The Forbidden Actions
- **NEVER** reuse or guess UUIDs. Always generate fresh ones.
- **NEVER** modify an existing UUID.
- **NEVER** create lessons without validation.py.
- **NEVER** place the Solution code in the Hint field.
- **NEVER** leave placeholder content (e.g., "Handle error").

# VI. Changelog
- **2026-02-06**: Updated to reflect UUID-based, directory-structured curriculum architecture. Added manifest.json documentation. Deprecated single-file JSON approach.

Proceed with the gravity this task deserves.
