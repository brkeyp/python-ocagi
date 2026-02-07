# -*- coding: utf-8 -*-
import os
import json
import importlib.util
import logging
import config

# Data classes for structured access
class Lesson:
    def __init__(self, data, path, numeric_id):
        self.slug = data.get('id') # String ID (e.g. 'basics_vars')
        self.uuid = data.get('uuid') # Stable UUID
        self.numeric_id = numeric_id # Integer ID for UI order
        self.category = data.get('category', 'Genel')
        self.title = data.get('title', 'Başlıksız')
        self.description = data.get('description', '')
        self.hint = data.get('hint', '')
        self.xp = data.get('xp', 10)
        self.tags = data.get('tags', [])
        
        # Validation Logic
        self.test_cases = data.get('test_cases', []) # For I/O validation
        self.type = data.get('type', 'code') # code, quiz, etc.
        
        # file system paths
        self.dir_path = os.path.dirname(path)
        self.task_file = path
        
        # Optional Python Scripts
        self.validator_script = os.path.join(self.dir_path, 'validation.py')
        self.solution_script = os.path.join(self.dir_path, 'solution.py')
        
        # Custom Solution
        self.solution_code = "" 
        if os.path.exists(self.solution_script):
             try:
                 with open(self.solution_script, 'r', encoding='utf-8') as f:
                     self.solution_code = f.read()
             except: pass
             
    def has_custom_validator(self):
        return os.path.exists(self.validator_script)

class CurriculumManager:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.lessons = [] # Ordered list of Lesson objects
        self.lesson_map = {} # slug -> Lesson
        self.id_map = {} # numeric_id -> Lesson
        self.manifest = {}
        
    def load(self):
        """Loads the entire curriculum from the file system."""
        self.lessons = []
        self.lesson_map = {}
        self.id_map = {}
        self.uuid_map = {} # uuid -> Lesson
        
        manifest_path = os.path.join(self.root_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            logging.warning("Manifest not found. Scanning directories blindly.")
            # Fallback scan (not implemented yet for simplicity, we assume manifest exists)
            return

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load manifest: {e}")
            return

        # Iterate chapters in order
        global_id_counter = 1
        
        if 'chapters' in self.manifest:
            for chapter in self.manifest['chapters']:
                chapter_slug = chapter.get('slug')
                chapter_path = os.path.join(self.root_dir, chapter_slug)
                
                if not os.path.exists(chapter_path):
                    continue
                    
                # Scan for lessons in this chapter
                # We look for folders that contain task.json
                # OR we look for a 'lessons' list in meta.json if we want strict ordering
                # For now, let's assume strict ordering via meta.json is better,
                # but filesystem sort is easier for dev. 
                # Let's try to read a local manifest in the chapter or sort folders.
                
                # Sorting folders alphabetically (e.g. 01_lesson, 02_lesson)
                try:
                    entries = sorted(os.listdir(chapter_path))
                except OSError:
                    continue
                    
                for entry in entries:
                    lesson_dir = os.path.join(chapter_path, entry)
                    task_file = os.path.join(lesson_dir, 'task.json')
                    
                    if os.path.isdir(lesson_dir) and os.path.exists(task_file):
                        try:
                            with open(task_file, 'r', encoding='utf-8') as f:
                                task_data = json.load(f)
                            
                            # Inject Category if missing
                            if 'category' not in task_data:
                                task_data['category'] = chapter.get('title', 'Genel')
                                
                            lesson = Lesson(task_data, task_file, global_id_counter)
                            
                            self.lessons.append(lesson)
                            self.lesson_map[lesson.slug] = lesson
                            self.id_map[global_id_counter] = lesson
                            if lesson.uuid:
                                self.uuid_map[lesson.uuid] = lesson
                            
                            global_id_counter += 1
                        except Exception as e:
                            logging.error(f"Error loading lesson {entry}: {e}")

    def get_lesson_by_id(self, numeric_id):
        # Legacy support: ID map is still populated but we should prefer UUIDs
        return self.id_map.get(numeric_id)

    def get_lesson_by_uuid(self, uuid_str):
        """Returns lesson by its stable UUID."""
        return self.uuid_map.get(uuid_str)

    def get_lesson_by_slug(self, slug):
        return self.lesson_map.get(slug)
    
    def get_next_lesson(self, current_uuid):
        """Returns the next lesson in the ordered list after the given UUID."""
        if current_uuid not in self.uuid_map:
            return None
            
        current_lesson = self.uuid_map[current_uuid]
        # Find index in the ordered list
        # Optimization: We could store index in Lesson but that duplicates state
        try:
            idx = self.lessons.index(current_lesson)
            if idx + 1 < len(self.lessons):
                return self.lessons[idx + 1]
        except ValueError:
            pass
        return None

    def get_prev_lesson(self, current_uuid):
        """Returns the previous lesson in the ordered list."""
        if current_uuid not in self.uuid_map:
            return None
            
        current_lesson = self.uuid_map[current_uuid]
        try:
            idx = self.lessons.index(current_lesson)
            if idx > 0:
                return self.lessons[idx - 1]
        except ValueError:
            pass
        return None

    def get_first_lesson(self):
        if self.lessons:
            return self.lessons[0]
        return None

    def get_total_lessons(self):
        return len(self.lessons)

    def get_validator_function(self, lesson):
        """
        Dynamically loads the validation function for a lesson.
        Returns: function(scope, output) -> bool/str
        """
        if not lesson.has_custom_validator():
            return None
            
        try:
            spec = importlib.util.spec_from_file_location("validation", lesson.validator_script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Expecting a 'Validator' class or 'validate' function
            if hasattr(module, 'validate'):
                return module.validate
            # Support class based too? Later.
            return None
        except Exception as e:
            logging.error(f"Failed to load validator for {lesson.slug}: {e}")
            return None
            
# Singleton Instance
# We will instantiate this in engine.py
