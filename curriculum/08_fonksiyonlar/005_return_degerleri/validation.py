def validate(scope, output):
    toplam = scope.get("toplam")
    carpim = scope.get("carpim")
    return toplam == 7 and carpim == 12
