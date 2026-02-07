def bilgi_yazdir(**kwargs):
    satirlar = []
    for anahtar, deger in kwargs.items():
        satirlar.append(f"{anahtar}: {deger}")
    return ', '.join(satirlar)

sonuc = bilgi_yazdir(ad='Ali', yas=25)
