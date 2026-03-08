def validate(scope, output):
        return str(scope.get("derece") or "").strip().lower() == "b"