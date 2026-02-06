def validate(scope, output):
        return scope.get("yil") == 2025 and isinstance(scope["yil"], int)