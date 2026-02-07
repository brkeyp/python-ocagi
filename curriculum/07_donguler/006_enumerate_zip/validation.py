def validate(scope, output):
    isimler = scope.get("isimler")
    yaslar = scope.get("yaslar")
    birlesik = scope.get("birlesik")
    
    if not isinstance(birlesik, list):
        return False
    
    expected = [('Ali', 20), ('Veli', 25), ('Ayşe', 22)]
    return birlesik == expected
