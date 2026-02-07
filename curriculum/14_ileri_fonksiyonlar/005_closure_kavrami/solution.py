def carpan_olustur(carpan):
    def carp(sayi):
        return sayi * carpan
    return carp

ikiyle_carp = carpan_olustur(2)
sonuc = ikiyle_carp(5)
