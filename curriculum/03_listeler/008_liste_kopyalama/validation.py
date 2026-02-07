def validate(scope, output):
    orijinal = scope.get("orijinal")
    kopya = scope.get("kopya")
    if kopya != [1, 2, 3]:
        return False
    # Check that they are different objects
    return orijinal is not kopya
