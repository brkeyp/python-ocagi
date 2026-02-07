class Araba:
    toplam_araba = 0
    
    def __init__(self):
        Araba.toplam_araba += 1

a1 = Araba()
a2 = Araba()
sayi = Araba.toplam_araba
