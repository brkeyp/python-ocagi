def validate(scope, output):
    # Old Validator ID: 20
    return scope.get("kimlik", {}).get("meslek") == "Mühendis"