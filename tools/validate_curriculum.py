#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Müfredat Doğrulama Aracı
Curriculum klasörünü tarayarak tutarsızlıkları tespit eder.
"""
import os
import json
import sys
import re

def validate_curriculum():
    """Müfredat bütünlüğünü doğrular."""
    base_dir = os.path.join(os.getcwd(), 'curriculum')
    uuids = {}
    lesson_ids = {}
    has_error = False
    has_warning = False
    stats = {'total': 0, 'errors': 0, 'warnings': 0}
    
    print(f"🔍 Müfredat taranıyor: {base_dir}")
    print("=" * 60)
    
    # Required fields in task.json
    required_fields = ['id', 'uuid', 'title', 'description']
    
    for root, dirs, files in os.walk(base_dir):
        if 'task.json' not in files:
            continue
            
        stats['total'] += 1
        path = os.path.join(root, 'task.json')
        folder_name = os.path.basename(root)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 1. Check required fields
            for field in required_fields:
                if not data.get(field):
                    print(f"❌ Eksik alan '{field}': {path}")
                    has_error = True
                    stats['errors'] += 1
            
            uid = data.get('uuid')
            lid = data.get('id')
            
            # 2. UUID uniqueness
            if uid:
                if uid in uuids:
                    print(f"❌ Çift UUID {uid}:")
                    print(f"   - {uuids[uid]}")
                    print(f"   - {path}")
                    has_error = True
                    stats['errors'] += 1
                else:
                    uuids[uid] = path
            
            # 3. ID uniqueness (per chapter)
            chapter = os.path.basename(os.path.dirname(root))
            full_id = f"{chapter}/{lid}"
            if lid:
                if full_id in lesson_ids:
                    print(f"❌ Çift ID {full_id}:")
                    print(f"   - {lesson_ids[full_id]}")
                    print(f"   - {path}")
                    has_error = True
                    stats['errors'] += 1
                else:
                    lesson_ids[full_id] = path
            
            # 4. Folder naming format (NNN_name)
            if not re.match(r'^\d{3}_', folder_name):
                print(f"⚠️  Klasör formatı yanlış (NNN_ olmalı): {folder_name}")
                has_warning = True
                stats['warnings'] += 1
            
            # 5. Check for validation.py
            val_path = os.path.join(root, 'validation.py')
            if not os.path.exists(val_path):
                print(f"❌ Eksik validation.py: {root}")
                has_error = True
                stats['errors'] += 1
            
            # 6. Check for solution.py
            sol_path = os.path.join(root, 'solution.py')
            if not os.path.exists(sol_path):
                print(f"❌ Eksik solution.py: {root}")
                has_error = True
                stats['errors'] += 1
            
            # 7. ID should match folder name
            if lid and lid != folder_name:
                print(f"⚠️  ID-klasör uyumsuzluğu: ID='{lid}' vs Klasör='{folder_name}'")
                has_warning = True
                stats['warnings'] += 1
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON hatası {path}: {e}")
            has_error = True
            stats['errors'] += 1
        except Exception as e:
            print(f"❌ Beklenmeyen hata {path}: {e}")
            has_error = True
            stats['errors'] += 1
    
    # Summary
    print("=" * 60)
    print(f"📊 Özet: {stats['total']} ders tarandı")
    print(f"   ❌ Hatalar: {stats['errors']}")
    print(f"   ⚠️  Uyarılar: {stats['warnings']}")
    
    if not has_error and not has_warning:
        print("\n✅ Müfredat Bütünlük Kontrolü BAŞARILI!")
        sys.exit(0)
    elif has_error:
        print("\n❌ Doğrulama BAŞARISIZ - Hatalar düzeltilmeli.")
        sys.exit(1)
    else:
        print("\n⚠️  Doğrulama UYARILARLA tamamlandı.")
        sys.exit(0)

if __name__ == "__main__":
    validate_curriculum()
