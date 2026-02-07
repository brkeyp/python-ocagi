def validate(scope, output):
        return scope.get("pi_sayisi") == 3.14 and isinstance(scope["pi_sayisi"], float)