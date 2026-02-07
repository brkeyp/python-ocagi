def validate(scope, output):
    gunler = scope.get("gunler")
    if not isinstance(gunler, frozenset):
        return False
    return gunler == frozenset({'pazartesi', 'sali', 'carsamba'})
