import json
def validate(scope, output):
    kisi = scope.get("kisi")
    json_str = scope.get("json_str")
    
    if not isinstance(json_str, str):
        return False
    
    # JSON string tekrar parse edilebilmeli
    parsed = json.loads(json_str)
    return parsed == {'ad': 'Ayşe', 'yas': 30}
