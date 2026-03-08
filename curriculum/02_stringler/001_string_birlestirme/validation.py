def validate(scope, output):
        return str(scope.get("tam_isim") or "").strip().lower() == "python kursu"