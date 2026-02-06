def validate(scope, output):
    Gorev = scope.get('Gorev')
    if not Gorev: return False
    
    # Check class instantiation
    try:
        t = Gorev("Test")
        if not hasattr(t, 'baslik') or not hasattr(t, 'durum'):
            return False
    except:
        return False
        
    # Check list
    gorevler = scope.get('gorevler')
    if not isinstance(gorevler, list) or len(gorevler) < 2:
        return False
        
    # Check elements validation
    return isinstance(gorevler[0], Gorev)