def validate(scope, output):
    a = scope.get("a")
    b = scope.get("b")
    birlesim = scope.get("birlesim")
    kesisim = scope.get("kesisim")
    
    if not all(isinstance(x, set) for x in [a, b, birlesim, kesisim] if x is not None):
        return False
    
    return birlesim == {1, 2, 3, 4, 5} and kesisim == {3}
