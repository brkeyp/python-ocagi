def validate(scope, output):
    topla = scope.get("topla")
    sonuc = scope.get("sonuc")
    
    if not callable(topla):
        return False
    
    return sonuc == 15
