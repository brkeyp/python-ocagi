def validate(scope, output):
    Hesap = scope.get("Hesap")
    if Hesap is None or not isinstance(Hesap, type):
        return False
    h = Hesap()
    h.para_yatir(100)
    return hasattr(h, '_bakiye') and h._bakiye == 100
