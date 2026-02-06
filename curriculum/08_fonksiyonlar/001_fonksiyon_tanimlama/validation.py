import types
def validate(scope, output):
        return isinstance(scope.get("kare_al"), types.FunctionType) and scope["kare_al"](5) == 25