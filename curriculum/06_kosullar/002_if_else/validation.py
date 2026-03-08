def validate(scope, output):
        return str(scope.get("sonuc") or "").strip().lower() == "tek"