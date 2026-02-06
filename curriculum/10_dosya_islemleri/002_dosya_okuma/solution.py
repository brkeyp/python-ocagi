# Test için dosyayı oluştur
with open('veri.txt', 'w') as f:
    f.write('örnek içerik')

dosya = open('veri.txt', 'r')
icerik = dosya.read()
dosya.close()
