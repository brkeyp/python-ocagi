def validate(scope, output):
    Dikdortgen = scope.get("Dikdortgen")
    if Dikdortgen is None:
        return False
    d = Dikdortgen(5, 4)
    return d.alan == 20
