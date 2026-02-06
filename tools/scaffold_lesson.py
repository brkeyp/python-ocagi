import os
import sys
import json
import uuid
import argparse

def create_lesson(chapter, slug, title, description):
    # Normalize paths
    base_dir = os.path.join(os.getcwd(), 'curriculum')
    chapter_dir = os.path.join(base_dir, chapter)
    
    if not os.path.exists(chapter_dir):
        print(f"Chapter '{chapter}' not found. Creating...")
        os.makedirs(chapter_dir)
        
    lesson_dir = os.path.join(chapter_dir, slug)
    if os.path.exists(lesson_dir):
        print(f"Lesson '{slug}' already exists!")
        return

    os.makedirs(lesson_dir)
    
    # Generate Task JSON
    task_data = {
        "id": slug,
        "uuid": str(uuid.uuid4()),
        "category": chapter.split('_', 1)[1].title().replace('_', ' '),
        "title": title,
        "description": description,
        "hint": "Bu bir otomatik oluşturulmuş derstir. Lütfen ipucunu düzenleyin.",
        "type": "code",
        "xp": 10,
        "tags": [chapter.split('_', 1)[1]]
    }
    
    with open(os.path.join(lesson_dir, 'task.json'), 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=4, ensure_ascii=False)
        
    # Generate Validation Template
    val_content = """def validate(scope, output):
    # TODO: Implement robust validation logic here
    # Example: Check if a variable exists and has value
    # return scope.get("x") == 10
    return False
"""
    with open(os.path.join(lesson_dir, 'validation.py'), 'w', encoding='utf-8') as f:
        f.write(val_content)
        
    # Generate Solution Template
    sol_content = """# Çözüm Kodu
# Buraya çalışan doğru kodu yazın
"""
    with open(os.path.join(lesson_dir, 'solution.py'), 'w', encoding='utf-8') as f:
        f.write(sol_content)

    print(f"✅ Lesson created: {lesson_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new lesson")
    parser.add_argument("chapter", help="Chapter folder name (e.g. 01_temeller)")
    parser.add_argument("slug", help="Lesson folder name (e.g. 050_yeni_ders)")
    parser.add_argument("title", help="Lesson Title")
    parser.add_argument("description", help="Lesson Description")
    
    args = parser.parse_args()
    create_lesson(args.chapter, args.slug, args.title, args.description)
