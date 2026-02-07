from functools import partial

def us_al(taban, us):
    return taban ** us

kare = partial(us_al, us=2)
sonuc = kare(5)
