def validate(scope, output):
    fiyat_listesi = scope.get("fiyat_listesi")
    if not isinstance(fiyat_listesi, list):
        return False
    return fiyat_listesi == [5, 7]
