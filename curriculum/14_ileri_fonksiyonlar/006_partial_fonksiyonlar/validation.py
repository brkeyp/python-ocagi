def validate(scope, output):
    kare = scope.get("kare")
    sonuc = scope.get("sonuc")
    
    if not callable(kare):
        return False
    
    return sonuc == 25
