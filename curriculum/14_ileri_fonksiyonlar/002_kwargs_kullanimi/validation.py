def validate(scope, output):
    bilgi_yazdir = scope.get("bilgi_yazdir")
    sonuc = scope.get("sonuc")
    
    if not callable(bilgi_yazdir):
        return False
    
    # Sonuçta her iki bilgi de olmalı
    return 'ad: Ali' in sonuc and 'yas: 25' in sonuc
