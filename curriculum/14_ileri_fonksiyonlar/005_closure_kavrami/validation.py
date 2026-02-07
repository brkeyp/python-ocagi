def validate(scope, output):
    ikiyle_carp = scope.get("ikiyle_carp")
    sonuc = scope.get("sonuc")
    
    if not callable(ikiyle_carp):
        return False
    
    return sonuc == 10
