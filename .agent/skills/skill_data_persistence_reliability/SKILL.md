---
name: Data Persistence & Reliability
description: The master protocol for saving, loading, verifying, and protecting user data against corruption and loss.
---

# PRIME DIRECTIVE: TOTAL CONTEXTUAL IMMERSION

**WARNING**: You are entering a zone of **Maximum Rigor**.
Data is sacred. A user's progress represents their time, their effort, and their emotional investment. Losing it is the ultimate failure.

Before attempting to modify the saving/loading logic:
1.  **Locate**: Search for functions named `save_progress`, `load_progress`, or similar. Find the JSON files storing the state.
2.  **Read**: Read the persistence module **in its entirety**.
3.  **Audit**: Check for "Atomic Write" patterns. Does it write to a `.tmp` file first?

**DO NOT PROCEED UNTIL YOU UNDERSTAND THE ATOMICITY GUARANTEE.**

---

# I. The Philosophy of Persistence
Filesystems are hostile. Power failures happen. Crashes happen.
Our philosophy is **Paranoia**.
- We never overwrite the live save file directly.
- We always assume the file might be corrupt on read.
- We always keep a backup.

# II. The Data Schema
The save file is likely a JSON object.
It typically contains:
- `current_step_id` (Integer)
- `completed_tasks` (List of Integers)
- `user_codes` (Dictionary: ID -> String)

**Sanitization**:
When loading data, **TRUST NOTHING**.
- Is `current_step_id` actually an int? If not, reset to 1.
- Is `completed_tasks` a list? If not, reset to `[]`.
- Is the JSON malformed? If so, load the backup.

# III. The Atomic Write Protocol
To save data safely, you must follow the ritual:
1.  **Serialize**: Convert the dictionary to a JSON string.
2.  **Write Temp**: Open `filename.json.tmp` and write the data.
3.  **Flush**: Call `file.flush()` to push data from python buffer to OS buffer.
4.  **Sync**: Call `os.fsync(fd)` to push data from OS buffer to physical disk.
5.  **Rename**: Call `os.replace(temp, original)`. This is atomic on POSIX and modern Windows.

If you skip step 4 or 5, you risk a 0-byte file on a power cut.

# IV. Protocol for Schema Evolution
When you need to add a new field to the save file (e.g., `xp_points`):

1.  **Default Value**:
    - Define a default value in the `get_default_progress()` function.

2.  **Migration Logic**:
    - In `load_progress()`, check if the key exists.
    - If missing (old save file), inject the default value.
    - **NEVER** crash because a key is missing.

# V. The Forbidden Actions
- **NEVER** use `open(file, 'w')` on the live file directly.
- **NEVER** leave a save file in an inconsistent state.
- **NEVER** store binary blobs if JSON suffices (human readability aids debugging).

Guard the data with your life.
