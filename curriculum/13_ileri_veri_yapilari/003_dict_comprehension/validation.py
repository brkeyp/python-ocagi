def validate(scope, output):
    kare_sozluk = scope.get("kare_sozluk")
    if not isinstance(kare_sozluk, dict):
        return False
    return kare_sozluk == {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
