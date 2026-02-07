def faktoriyel(n):
    if n <= 1:
        return 1
    return n * faktoriyel(n - 1)

sonuc = faktoriyel(5)
