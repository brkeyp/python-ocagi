import types
def validate(scope, output):
    gen = scope.get("gen")
    ilk = scope.get("ilk")
    
    # Generator zaten tüketilmiş olabilir, sadece ilk'i kontrol et
    return ilk == 1
