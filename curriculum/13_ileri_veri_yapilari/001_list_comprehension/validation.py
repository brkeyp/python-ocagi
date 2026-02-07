def validate(scope, output):
    kareler = scope.get("kareler")
    if not isinstance(kareler, list):
        return False
    return kareler == [1, 4, 9, 16, 25]
