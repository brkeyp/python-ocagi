import types
def validate(scope, output):
    # Old Validator ID: 27
    return isinstance(scope.get("kare_al"), types.FunctionType) and scope["kare_al"](5) == 25