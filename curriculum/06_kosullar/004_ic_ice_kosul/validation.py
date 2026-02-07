def validate(scope, output):
    yas = scope.get("yas")
    ehliyet = scope.get("ehliyet")
    sonuc = scope.get("sonuc")
    
    if yas != 25 or ehliyet != True:
        return False
    
    return sonuc == 'Araba kullanabilir'
