def validate(scope, output):
    fiyatlar = scope.get("fiyatlar")
    toplam = scope.get("toplam")
    
    if not isinstance(fiyatlar, dict):
        return False
    
    return toplam == 22
