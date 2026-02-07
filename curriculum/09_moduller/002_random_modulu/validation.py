def validate(scope, output):
    zar = scope.get("zar")
    if not isinstance(zar, int):
        return False
    return 1 <= zar <= 6
