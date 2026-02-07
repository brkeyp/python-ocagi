def validate(scope, output):
    YasHatasi = scope.get("YasHatasi")
    if YasHatasi is None:
        return False
    if not isinstance(YasHatasi, type):
        return False
    return issubclass(YasHatasi, Exception)
