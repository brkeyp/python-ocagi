def validate(scope, output):
    """Validates file reading task."""
    if 'icerik' not in scope:
        return False
    
    # The content should be a string
    if not isinstance(scope['icerik'], str):
        return False
    
    return True
