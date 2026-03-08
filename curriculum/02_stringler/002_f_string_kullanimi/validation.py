def validate(scope, output):
        return str(scope.get("kisi_bilgisi") or "").strip().lower() == "yaşım: 25"