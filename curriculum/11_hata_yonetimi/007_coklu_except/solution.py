def hesapla(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Sıfıra bölme!"
    except TypeError:
        return "Tip hatası!"
