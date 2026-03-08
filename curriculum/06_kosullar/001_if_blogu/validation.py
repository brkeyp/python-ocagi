def validate(scope, output):
        return str(scope.get("durum") or "").strip().lower() == "geçti"