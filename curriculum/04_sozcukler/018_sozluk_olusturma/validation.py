def validate(scope, output):
    # Old Validator ID: 18
    return scope.get("kimlik") == {'ad': 'Ali', 'yas': 30}