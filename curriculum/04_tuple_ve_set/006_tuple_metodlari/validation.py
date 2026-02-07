def validate(scope, output):
    notlar = scope.get("notlar")
    sayi = scope.get("sayi")
    konum = scope.get("konum")
    
    if not isinstance(notlar, tuple):
        return False
    
    return sayi == 3 and konum == 1
