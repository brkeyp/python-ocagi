def validate(scope, output):
    ogrenci = scope.get("ogrenci")
    anahtarlar = scope.get("anahtarlar")
    degerler = scope.get("degerler")
    
    if not isinstance(ogrenci, dict):
        return False
    if not isinstance(anahtarlar, list) or not isinstance(degerler, list):
        return False
    
    return set(anahtarlar) == {'ad', 'yas', 'sinif'} and set(degerler) == {'Ali', 20, '3A'}
