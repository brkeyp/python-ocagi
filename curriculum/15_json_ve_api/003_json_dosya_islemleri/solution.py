ogrenciler = [{'ad': 'Ali', 'not': 85}, {'ad': 'Veli', 'not': 90}]
en_iyi = max(ogrenciler, key=lambda x: x['not'])
en_yuksek = en_iyi['ad']
