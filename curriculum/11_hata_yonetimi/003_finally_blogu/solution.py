temizlik_yapildi = False

try:
    sonuc = 10 / 2
except ZeroDivisionError:
    pass
finally:
    temizlik_yapildi = True
