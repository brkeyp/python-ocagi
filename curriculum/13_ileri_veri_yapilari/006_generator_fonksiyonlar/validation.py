def validate(scope, output):
    sayac = scope.get("sayac")
    sonuclar = scope.get("sonuclar")
    
    if not callable(sayac):
        return False
    if not isinstance(sonuclar, list):
        return False
    
    return sonuclar == [1, 2, 3]
