import types
def validate(scope, output):
    topla = scope.get("topla")
    if not isinstance(topla, types.FunctionType):
        return False
    if topla.__doc__ is None:
        return False
    return "İki sayıyı toplar" in topla.__doc__
