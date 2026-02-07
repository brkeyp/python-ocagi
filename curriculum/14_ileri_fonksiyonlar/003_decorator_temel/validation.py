def validate(scope, output):
    selamla = scope.get("selamla")
    
    if not callable(selamla):
        return False
    
    return selamla() == 'MERHABA'
