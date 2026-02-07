def validate(scope, output):
    veri = scope.get("veri")
    if not isinstance(veri, dict):
        return False
    return veri == {"ad": "Ali", "yas": 25}
