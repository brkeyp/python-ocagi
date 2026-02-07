def topla(*args):
    toplam = 0
    for sayi in args:
        toplam = toplam + sayi
    return toplam

sonuc = topla(1, 2, 3, 4, 5)
