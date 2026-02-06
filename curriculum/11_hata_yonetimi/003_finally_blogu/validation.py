def validate(scope, output):
    """Validates finally block usage."""
    if 'temizlik_yapildi' not in scope:
        return False
    return scope['temizlik_yapildi'] is True
