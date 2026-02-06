def validate(scope, output):
    # Old Validator ID: 2
    return scope.get("yil") == 2025 and isinstance(scope["yil"], int)