def validate(scope, output):
    # Check VFS via scope['open']
    try:
        # scope['open'] is fs.open (bound method)
        fs = scope['open'].__self__
        return fs.exists('test.txt')
    except:
        return False