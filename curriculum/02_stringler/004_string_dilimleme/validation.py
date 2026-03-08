def validate(scope, output):
        return str(scope.get("ilk_uc") or "").strip().lower() == "abc"