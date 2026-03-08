def validate(scope, output):
        return str(scope.get("isim_degeri") or "").strip().lower() == "ali"