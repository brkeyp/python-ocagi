def validate(scope, output):
    okul = scope.get("okul")
    mevcudiyet = scope.get("mevcudiyet")
    
    if not isinstance(okul, dict):
        return False
    
    return mevcudiyet == 25
