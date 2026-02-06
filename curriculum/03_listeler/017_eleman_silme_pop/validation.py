def validate(scope, output):
    # Old Validator ID: 17
    return scope.get("liste") == [1, 2, 3, 4]