def validate(scope, output):
    sayi = scope.get("sayi")
    tip = scope.get("tip")
    
    if sayi != 15:
        return False
    
    return tip == 'tek'
