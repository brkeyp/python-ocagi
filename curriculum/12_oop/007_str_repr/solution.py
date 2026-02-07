class Kitap:
    def __init__(self, baslik):
        self.baslik = baslik
    
    def __str__(self):
        return f"Kitap: {self.baslik}"
