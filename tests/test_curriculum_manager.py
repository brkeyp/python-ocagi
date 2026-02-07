# -*- coding: utf-8 -*-
"""
Tests for CurriculumManager module.
"""
import pytest
import sys
import os
import json

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from curriculum_manager import CurriculumManager, Lesson


class TestLesson:
    """Tests for Lesson class."""
    
    def test_lesson_creation(self, tmp_path):
        """Test creating a Lesson with all fields."""
        lesson_dir = tmp_path / "lesson"
        lesson_dir.mkdir()
        task_file = lesson_dir / "task.json"
        
        data = {
            "uuid": "test-uuid-1234",
            "id": "01_test_lesson",
            "category": "Temel",
            "title": "Test Lesson",
            "description": "Test description",
            "hint": "Test hint"
        }
        task_file.write_text(json.dumps(data), encoding="utf-8")
        
        lesson = Lesson(data, str(task_file), numeric_id=1)
        
        assert lesson.uuid == "test-uuid-1234"
        assert lesson.slug == "01_test_lesson"
        assert lesson.numeric_id == 1
        assert lesson.title == "Test Lesson"
    
    def test_lesson_with_solution(self, tmp_path):
        """Test Lesson loads solution code."""
        lesson_dir = tmp_path / "lesson"
        lesson_dir.mkdir()
        task_file = lesson_dir / "task.json"
        solution_file = lesson_dir / "solution.py"
        
        data = {"uuid": "uuid-sol", "id": "sol_lesson", "title": "With Solution"}
        task_file.write_text(json.dumps(data), encoding="utf-8")
        solution_file.write_text("print('hello')", encoding="utf-8")
        
        lesson = Lesson(data, str(task_file), numeric_id=1)
        
        assert lesson.solution_code == "print('hello')"
    
    def test_lesson_defaults(self, tmp_path):
        """Test Lesson uses defaults for missing fields."""
        lesson_dir = tmp_path / "lesson"
        lesson_dir.mkdir()
        task_file = lesson_dir / "task.json"
        
        data = {"uuid": "uuid-minimal", "id": "minimal"}
        task_file.write_text(json.dumps(data), encoding="utf-8")
        
        lesson = Lesson(data, str(task_file), numeric_id=1)
        
        assert lesson.category == "Genel"
        assert lesson.title == "Başlıksız"
        assert lesson.xp == 10


class TestCurriculumManager:
    """Tests for CurriculumManager class."""
    
    @pytest.fixture
    def mock_curriculum(self, tmp_path):
        """Create a mock curriculum directory structure."""
        curriculum_dir = tmp_path / "curriculum"
        curriculum_dir.mkdir()
        
        # Create manifest.json
        manifest = {
            "chapters": [
                {"slug": "01_temeller", "title": "Temeller"},
                {"slug": "02_stringler", "title": "Stringler"}
            ]
        }
        (curriculum_dir / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        
        # Create chapter 1 with lessons
        chapter1 = curriculum_dir / "01_temeller"
        chapter1.mkdir()
        
        lesson1 = chapter1 / "001_first_lesson"
        lesson1.mkdir()
        (lesson1 / "task.json").write_text(json.dumps({
            "id": "001_first_lesson",
            "uuid": "uuid-first-lesson",
            "category": "Temel",
            "title": "First Lesson",
            "description": "First description",
            "hint": "First hint"
        }), encoding="utf-8")
        (lesson1 / "validation.py").write_text(
            "def validate(scope, output): return True"
        )
        (lesson1 / "solution.py").write_text("print('hello')")
        
        lesson2 = chapter1 / "002_second_lesson"
        lesson2.mkdir()
        (lesson2 / "task.json").write_text(json.dumps({
            "id": "002_second_lesson",
            "uuid": "uuid-second-lesson",
            "category": "Temel",
            "title": "Second Lesson",
            "description": "Second description"
        }), encoding="utf-8")
        (lesson2 / "validation.py").write_text(
            "def validate(scope, output): return True"
        )
        
        return curriculum_dir
    
    def test_load_curriculum(self, mock_curriculum):
        """Test loading curriculum from directory."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()  # Must call load() explicitly
        
        # Should have loaded 2 lessons
        assert len(manager.lessons) == 2
    
    def test_get_lesson_by_uuid(self, mock_curriculum):
        """Test retrieving lesson by UUID."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        lesson = manager.get_lesson_by_uuid("uuid-first-lesson")
        assert lesson is not None
        assert lesson.title == "First Lesson"
        
        # Non-existent UUID
        assert manager.get_lesson_by_uuid("non-existent") is None
    
    def test_get_lesson_by_slug(self, mock_curriculum):
        """Test retrieving lesson by slug."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        lesson = manager.get_lesson_by_slug("001_first_lesson")
        assert lesson is not None
        assert lesson.uuid == "uuid-first-lesson"
    
    def test_get_lesson_by_id(self, mock_curriculum):
        """Test retrieving lesson by numeric ID."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        lesson = manager.get_lesson_by_id(1)
        assert lesson is not None
        assert lesson.numeric_id == 1
    
    def test_lesson_order(self, mock_curriculum):
        """Test that lessons are loaded in correct order."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        assert manager.lessons[0].slug == "001_first_lesson"
        assert manager.lessons[1].slug == "002_second_lesson"
    
    def test_get_first_lesson(self, mock_curriculum):
        """Test getting the first lesson."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        first = manager.get_first_lesson()
        assert first is not None
        assert first.numeric_id == 1
    
    def test_empty_curriculum(self, tmp_path):
        """Test handling empty curriculum."""
        curriculum_dir = tmp_path / "curriculum"
        curriculum_dir.mkdir()
        (curriculum_dir / "manifest.json").write_text(
            json.dumps({"chapters": []}), 
            encoding="utf-8"
        )
        
        manager = CurriculumManager(str(curriculum_dir))
        manager.load()
        
        assert len(manager.lessons) == 0
        assert manager.get_first_lesson() is None
    
    def test_get_total_lessons(self, mock_curriculum):
        """Test get_total_lessons method."""
        manager = CurriculumManager(str(mock_curriculum))
        manager.load()
        
        assert manager.get_total_lessons() == 2
