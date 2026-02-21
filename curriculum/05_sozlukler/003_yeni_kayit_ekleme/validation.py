def validate(scope, output):
        return scope.get("kimlik", {}).get("meslek") == "Mühendis"