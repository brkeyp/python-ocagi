import types
def validate(scope, output):
    func = scope.get("yas_kontrol")
    if not isinstance(func, types.FunctionType):
        return False
    try:
        result = func(-5)
        return False  # Should have raised
    except ValueError as e:
        if "negatif" not in str(e).lower():
            return False
    return func(25) == 25
