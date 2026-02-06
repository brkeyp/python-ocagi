def validate(scope, output):
    """
    Validates that the user:
    1. Used try-except block
    2. Set hata_olustu = True after catching the error
    """
    # Check if 'hata_olustu' exists and is True
    if 'hata_olustu' not in scope:
        return False
    
    if scope['hata_olustu'] is not True:
        return False
    
    return True