def validate(scope, output):
        return str(scope.get("mesaj") or "").strip().lower() == "merhaba dünya"