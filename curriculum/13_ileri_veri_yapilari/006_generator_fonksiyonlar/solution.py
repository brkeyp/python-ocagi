def sayac(n):
    for i in range(1, n + 1):
        yield i

sonuclar = list(sayac(3))
