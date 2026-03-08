import types
def validate(scope, output):
    topla = scope.get("topla")
    if not isinstance(topla, types.FunctionType):
        return False
    if topla.__doc__ is None:
        return False
        
    doc = topla.__doc__.lower()
    return len(doc.strip()) > 5 or ("topla" in doc)
