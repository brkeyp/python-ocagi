def validate(scope, output):
    """Validates specific exception handling."""
    if 'bolme_hatasi' not in scope:
        return False
    return scope['bolme_hatasi'] is True
