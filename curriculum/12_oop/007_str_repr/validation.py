def validate(scope, output):
    Kitap = scope.get("Kitap")
    if Kitap is None:
        return False
    k = Kitap("Python 101")
    return str(k) == "Kitap: Python 101"
