def validate(scope, output):
        return str(scope.get("sehir_buyuk") or "").strip().lower() == "istanbul"