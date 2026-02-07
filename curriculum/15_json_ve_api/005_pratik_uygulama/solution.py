import json
envanter = '[{"urun": "Kalem", "adet": 50}, {"urun": "Defter", "adet": 30}]'
liste = json.loads(envanter)
toplam_adet = sum(x['adet'] for x in liste)
