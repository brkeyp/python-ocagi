def validate(scope, output):
    if 'simdi' not in scope: return False
    import datetime
    return isinstance(scope['simdi'], datetime.datetime)
