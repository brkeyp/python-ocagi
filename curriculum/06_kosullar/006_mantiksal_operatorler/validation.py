def validate(scope, output):
    sicaklik = scope.get("sicaklik")
    yagmurlu = scope.get("yagmurlu")
    hava = scope.get("hava")
    
    if sicaklik != 25 or yagmurlu != False:
        return False
    
    return hava == 'Piknik zamanı!'
