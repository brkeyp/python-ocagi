def validate(scope, output):
    if scope.get("sayi_str") != "100":
        return False
    if scope.get("sayi_int") != 100:
        return False
    return type(scope.get("sayi_int")) == int
