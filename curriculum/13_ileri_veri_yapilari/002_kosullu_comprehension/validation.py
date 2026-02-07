def validate(scope, output):
    ciftler = scope.get("ciftler")
    if not isinstance(ciftler, list):
        return False
    return ciftler == [2, 4, 6, 8, 10]
