def validate(scope, output):
    harfler = scope.get("harfler")
    if not isinstance(harfler, set):
        return False
    return harfler == {'m', 'e', 'r', 'h', 'a', 'b'}
