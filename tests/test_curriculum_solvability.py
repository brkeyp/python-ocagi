# -*- coding: utf-8 -*-
"""
Müfredat Çözülebilirlik Testi
Tüm derslerin çözümlerinin doğrulayıcıları geçtiğini kontrol eder.
"""
import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from curriculum_manager import CurriculumManager
from sandbox.executor import run_safe


@pytest.fixture(scope="module")
def curriculum():
    """Load curriculum once for all tests."""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'curriculum')
    cm = CurriculumManager(base_dir)
    cm.load()
    return cm


@pytest.mark.slow
def test_all_lessons_have_required_files(curriculum):
    """Her dersin task.json dosyası olmalı."""
    for lesson in curriculum.lessons:
        assert lesson.uuid, f"{lesson.slug} has no UUID"
        assert lesson.title, f"{lesson.slug} has no title"


@pytest.mark.slow
def test_all_solutions_pass_validation(curriculum):
    """
    Tüm çözümlerin doğrulayıcıları geçtiğini kontrol eder.
    Bu test yavaş olabilir çünkü her dersi sandbox'ta çalıştırır.
    """
    failed = []
    
    for lesson in curriculum.lessons:
        # Skip if no solution file
        if not lesson.solution_code:
            continue
            
        result = run_safe(lesson.solution_code, lesson.validator_script, timeout=2.0)
        
        if not result['is_valid']:
            failed.append({
                'slug': lesson.slug,
                'error': result.get('error_message'),
                'stdout': result.get('stdout')
            })
    
    if failed:
        failure_msg = "\n".join([
            f"- {f['slug']}: {f['error']}" for f in failed
        ])
        pytest.fail(f"The following lessons failed validation:\n{failure_msg}")


def test_no_duplicate_uuids(curriculum):
    """UUID'ler benzersiz olmalı."""
    uuids = [lesson.uuid for lesson in curriculum.lessons]
    duplicates = [uuid for uuid in uuids if uuids.count(uuid) > 1]
    assert len(duplicates) == 0, f"Duplicate UUIDs found: {set(duplicates)}"


def test_curriculum_has_lessons(curriculum):
    """Müfredat en az bir ders içermeli."""
    assert len(curriculum.lessons) > 0, "Curriculum has no lessons"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
