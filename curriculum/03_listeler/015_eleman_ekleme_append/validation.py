def validate(scope, output):
    # Old Validator ID: 15
    return scope.get("renkler") == ["Mavi", "Yesil"]