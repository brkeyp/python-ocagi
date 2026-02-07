class Dikdortgen:
    def __init__(self, genislik, yukseklik):
        self.genislik = genislik
        self.yukseklik = yukseklik
    
    @property
    def alan(self):
        return self.genislik * self.yukseklik
