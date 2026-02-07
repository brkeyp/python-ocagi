def validate(scope, output):
    carpim = scope.get("carpim")
    if not isinstance(carpim, list):
        return False
    return carpim == [1, 2, 3, 2, 4, 6]
