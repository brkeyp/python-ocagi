import types
def validate(scope, output):
    func = scope.get("hesapla")
    if not isinstance(func, types.FunctionType):
        return False
    r1 = func(10, 0)
    r2 = func("a", 2)
    return "Sıfıra bölme" in r1 and "Tip hatası" in r2
