def validate(scope, output):
    # Old Validator ID: 37
    return scope.get("kareler") == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]