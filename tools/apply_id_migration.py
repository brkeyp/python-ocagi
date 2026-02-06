# -*- coding: utf-8 -*-
"""
ID Migration Tool for Python Kurs Simülatörü
--------------------------------------------
This script performs a one-time migration to:
1. Inject stable UUIDs into all task.json files.
2. Update progress.json to use UUIDs instead of integer IDs.

Usage:
    python tools/apply_id_migration.py
"""

import os
import json
import uuid
import shutil
import logging
import sys

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRICULUM_DIR = os.path.join(BASE_DIR, 'curriculum')
PROGRESS_FILE = os.path.join(BASE_DIR, 'progress.json')
BACKUP_FILE = os.path.join(BASE_DIR, 'progress.json.migration_backup')

def load_manifest():
    manifest_path = os.path.join(CURRICULUM_DIR, 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Manifest loading failed: {e}")
        return None

def migrate_curriculum():
    """
    Iterates through the curriculum in the EXACT SAME ORDER as the old engine.
    Assigns UUIDs and builds a mapping from Old ID (int) -> New ID (uuid).
    """
    manifest = load_manifest()
    if not manifest:
        return None

    id_mapping = {} # int -> uuid_str
    global_counter = 1
    
    # 1. Iterate Chapters
    if 'chapters' in manifest:
        for chapter in manifest['chapters']:
            chapter_slug = chapter.get('slug')
            chapter_path = os.path.join(CURRICULUM_DIR, chapter_slug)
            
            if not os.path.exists(chapter_path):
                continue
                
            # 2. Iterate Leesons (Sorted Alphabetically - Critical for ordering match)
            try:
                entries = sorted(os.listdir(chapter_path))
            except OSError:
                continue
                
            for entry in entries:
                lesson_dir = os.path.join(chapter_path, entry)
                task_file = os.path.join(lesson_dir, 'task.json')
                
                if os.path.isdir(lesson_dir) and os.path.exists(task_file):
                    # Process Task
                    try:
                        with open(task_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Generate or Reuse UUID
                        if 'uuid' in data:
                            task_uuid = data['uuid']
                            logging.info(f"Existing UUID found for {entry}: {task_uuid}")
                        else:
                            task_uuid = str(uuid.uuid4())
                            data['uuid'] = task_uuid
                            # Write back
                            with open(task_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            logging.info(f"Injecting UUID for {entry} (ID: {global_counter}) -> {task_uuid}")
                        
                        # Store Mapping
                        id_mapping[global_counter] = task_uuid
                        global_counter += 1
                        
                    except Exception as e:
                        logging.error(f"Error processing {entry}: {e}")
                        
    return id_mapping

def migrate_progress(id_mapping):
    """
    Updates progress.json using the mapping.
    """
    if not os.path.exists(PROGRESS_FILE):
        logging.info("No progress file found. Skipping data migration.")
        return

    # Backup
    shutil.copy2(PROGRESS_FILE, BACKUP_FILE)
    logging.info(f"Progress backed up to {BACKUP_FILE}")
    
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Migrate 'completed_tasks' (List of Ints -> List of UUIDs)
        new_completed = []
        for old_id in data.get('completed_tasks', []):
            if old_id in id_mapping:
                new_completed.append(id_mapping[old_id])
            else:
                logging.warning(f"Unknown ID in completed_tasks: {old_id}")
        data['completed_tasks'] = new_completed
        
        # Migrate 'skipped_tasks'
        new_skipped = []
        for old_id in data.get('skipped_tasks', []):
            if old_id in id_mapping:
                new_skipped.append(id_mapping[old_id])
        data['skipped_tasks'] = new_skipped
        
        # Migrate 'user_code' (Dict Key IntStr -> UUID)
        new_user_code = {}
        for old_id_str, code in data.get('user_code', {}).items():
            try:
                old_id = int(old_id_str)
                if old_id in id_mapping:
                    new_user_code[id_mapping[old_id]] = code
            except ValueError:
                pass
        data['user_code'] = new_user_code
        
        # Migrate 'current_step'
        old_current = data.get('current_step', 1)
        if old_current in id_mapping:
            data['current_step'] = id_mapping[old_current]
        else:
            # Default to first available UUID if current is invalid
            if id_mapping:
                data['current_step'] = id_mapping[1]
                logging.warning(f"Current step {old_current} not found. Resetting to start.")
            else:
                 data['current_step'] = None

        # Handle 'highest_reached_id' -> 'highest_reached_index'
        # Since we are moving to UUIDs, we can't easily compare "Greater Than".
        # For now, let's remove it or convert it to an index if we decide to keep linear progression enforcement.
        # Decision: Convert to 'latest_unlocked_index' for internal logic, or just assume the 'current_step' uuid implies position.
        # For safety, let's just delete it for now and handle logic in Engine.
        if 'highest_reached_id' in data:
            del data['highest_reached_id']
            
        # Save
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logging.info("Progress.json migrated successfully.")
        
    except Exception as e:
        logging.error(f"Error migrating progress: {e}")
        # Restore backup
        shutil.copy2(BACKUP_FILE, PROGRESS_FILE)
        logging.info("Restored backup due to error.")

if __name__ == "__main__":
    print("Starting ID Migration...")
    mapping = migrate_curriculum()
    if mapping:
        print(f"Mapped {len(mapping)} tasks.")
        migrate_progress(mapping)
        print("Migration Complete.")
    else:
        print("Failed to map curriculum.")
