def validate(scope, output):
        return str(scope.get("ses") or "").strip().lower() == "hav!"