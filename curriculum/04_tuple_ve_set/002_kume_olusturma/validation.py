def validate(scope, output):
    renkler = scope.get("renkler")
    if not isinstance(renkler, set):
        return False
    return renkler == {'kirmizi', 'yesil', 'mavi'}
