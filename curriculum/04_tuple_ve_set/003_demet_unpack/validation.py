def validate(scope, output):
    """Validates tuple unpacking."""
    if 'enlem' not in scope or 'boylam' not in scope:
        return False
    
    try:
        if abs(scope['enlem'] - 35.6762) < 0.0001 and \
           abs(scope['boylam'] - 139.6503) < 0.0001:
            return True
    except (TypeError, ValueError):
        return False
    
    return False
