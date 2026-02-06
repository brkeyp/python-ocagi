def validate(scope, output):
    # Old Validator ID: 3
    return scope.get("pi_sayisi") == 3.14 and isinstance(scope["pi_sayisi"], float)