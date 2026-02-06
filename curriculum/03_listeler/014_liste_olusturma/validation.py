def validate(scope, output):
    # Old Validator ID: 14
    return scope.get("sayilar") == [10, 20, 30]