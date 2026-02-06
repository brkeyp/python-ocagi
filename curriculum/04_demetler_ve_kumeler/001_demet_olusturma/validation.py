def validate(scope, output):
    """
    Validates that the user created a tuple named 'koordinatlar'
    with the correct values.
    """
    # Check if 'koordinatlar' exists
    if 'koordinatlar' not in scope:
        return False
    
    koordinatlar = scope['koordinatlar']
    
    # Check if it's a tuple
    if not isinstance(koordinatlar, tuple):
        return False
    
    # Check if it has exactly 2 elements
    if len(koordinatlar) != 2:
        return False
    
    # Check the values (with floating point tolerance)
    expected = (40.7128, -74.0060)
    
    try:
        if abs(koordinatlar[0] - expected[0]) < 0.0001 and \
           abs(koordinatlar[1] - expected[1]) < 0.0001:
            return True
    except (TypeError, IndexError):
        return False
    
    return False
