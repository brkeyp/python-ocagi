def validate(scope, output):
    en_yuksek = scope.get("en_yuksek")
    return str(en_yuksek or "").strip().lower() == "veli"
