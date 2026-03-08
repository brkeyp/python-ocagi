def validate(scope, output):
        return str(scope.get("ortadaki") or "").strip().lower() == "armut"