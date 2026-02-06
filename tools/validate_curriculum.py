import os
import json
import sys

def validate_curriculum():
    base_dir = os.path.join(os.getcwd(), 'curriculum')
    uuids = {}
    has_error = False
    
    print(f"Scanning {base_dir}...")
    
    for root, dirs, files in os.walk(base_dir):
        if 'task.json' in files:
            path = os.path.join(root, 'task.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                uid = data.get('uuid')
                lid = data.get('id')
                
                if not uid:
                    print(f"❌ Missing UUID: {path}")
                    has_error = True
                    continue
                    
                if uid in uuids:
                    print(f"❌ Duplicate UUID {uid} in:")
                    print(f"   - {uuids[uid]}")
                    print(f"   - {path}")
                    has_error = True
                else:
                    uuids[uid] = path
                    
                # Check for validation.py
                val_path = os.path.join(root, 'validation.py')
                if not os.path.exists(val_path):
                     print(f"⚠️  Missing validation.py: {path}")
                     # Not a hard error yet, but bad practice
                
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
                has_error = True

    if not has_error:
        print("✅ Curriculum Integrity Check Passed!")
        sys.exit(0)
    else:
        print("❌ Validation Failed.")
        sys.exit(1)

if __name__ == "__main__":
    validate_curriculum()
