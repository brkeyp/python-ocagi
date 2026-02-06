def validate(scope, output):
    pk = scope.get('Canli')
    ck = scope.get('Insan')
    if not pk or not ck: return False
    return issubclass(ck, pk)
