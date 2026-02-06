def validate(scope, output):
    if 'adres' not in scope: return False
    return isinstance(scope['adres'], str) and len(scope['adres']) > 0
