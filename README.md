# 🐍 Python Ocağı

Terminal tabanlı, interaktif Python öğrenme platformu.

## ✨ Özellikler

- 🎓 **98 Ders** - 16 bölüm boyunca kapsamlı Python müfredatı
- 🔒 **Güvenli Sandbox** - Kullanıcı kodu izole çalışır
- 🎨 **Syntax Highlighting** - Gerçek zamanlı renklendirme
- 📊 **İlerleme Takibi** - Tamamlanan ve atlanan görevler kaydedilir
- 🌈 **Türkçe Arayüz** - Tamamen Türkçe kullanıcı deneyimi

## 🚀 Hızlı Kurulum (Sıfır Zahmet)

Uygulamayı kurmak ve otomatik olarak her zaman güncel kalmasını sağlamak için, işletim sisteminize uygun olan aşağıdaki **tek satırlık sihirli komutu** kopyalayıp bilgisayarınızın siyah ekranına (Terminal/PowerShell) yapıştırıp ENTER'a basmanız yeterlidir.

### 🪟 Windows İçin
PowerShell programını açın (Başlat menüsüne "powershell" yazabilirsiniz) ve şu komutu yapıştırın:
```powershell
iex (iwr -useb https://raw.githubusercontent.com/brkeyp/python-ocagi/main/kur_windows.ps1)
```
*(Eğer sisteminizde Python yoksa sizin için otomatik olarak indirip kuracaktır. Masaüstünüze oluşturulan "PYTHON OCAĞINA GİR" dosyası ile programı dilediğiniz zaman başlatabilirsiniz).*

### 🍎 Mac ve 🐧 Linux İçin
Terminal programını açın ve şu komutu yapıştırın:
```bash
curl -sL https://raw.githubusercontent.com/brkeyp/python-ocagi/main/kur_unix.sh | bash
```
*(Masaüstünüze oluşturulan "PYTHON OCAĞINA GİR" dosyası ile programı dilediğiniz zaman başlatabilirsiniz).*

## 🎮 Kullanım

### Klavye Kısayolları

| Tuş | İşlev |
|-----|-------|
| `Enter (x2)` | Kodu gönder / Soruyu atla |
| `Alt+←/→` | Önceki/Sonraki soru |
| `?` | İpucu göster/gizle |
| `Del` | İlerlemeyi sıfırla |
| `Ctrl+C` | Çıkış |
| `ESC+VAO` | Geliştirici mesajı |

### Ekran Yapısı

```
┌─────────────────────────────────────┐
│  🐍 Python Ocağı          │
├─────────────────────────────────────┤
│  BÖLÜM:     Temeller                │
│  GÖREV 1:   Print Fonksiyonu        │
├─────────────────────────────────────┤
│  SORU: print() ile "Merhaba"        │
│        yazdırın.                    │
├─────────────────────────────────────┤
│  > print("Merhaba")_                │
│                                     │
├─────────────────────────────────────┤
│  ESC+VAO · ? İpucu · Alt+← Geç      │
└─────────────────────────────────────┘
```

## 📚 Müfredat

| Bölüm | Konu | Ders Sayısı |
|-------|------|-------------|
| 1 | Temeller | 12 |
| 2 | Stringler | 5 |
| 3 | Listeler | 9 |
| 4 | Tuple ve Set | 6 |
| 5 | Sözlükler | 6 |
| 6 | Koşullu İfadeler | 6 |
| 7 | Döngüler | 6 |
| 8 | Fonksiyonlar | 8 |
| 9 | Modüller | 4 |
| 10 | Dosya İşlemleri | 3 |
| 11 | Hata Yönetimi | 7 |
| 12 | OOP | 8 |
| 13 | İleri Veri Yapıları | 6 |
| 14 | İleri Fonksiyonlar | 6 |
| 15 | JSON ve API | 5 |
| 16 | Final Projesi | 1 |

## 🛠️ Geliştirme

### Test Çalıştırma

```bash
python3 -m pytest tests/ -v
```

### Müfredat Doğrulama

```bash
python3 tools/validate_curriculum.py
```

### Yeni Ders Ekleme

```bash
python3 tools/scaffold_lesson.py <bölüm> <ders_adı>
```

## 📁 Proje Yapısı

```
├── main.py              # Giriş noktası
├── engine.py            # Simülasyon motoru
├── controller.py        # Ana döngü
├── ui.py                # Kod editörü
├── ui_renderer.py       # Görsel rendering
├── sandbox.py           # Güvenlik katmanı
├── safe_runner.py       # Kod çalıştırıcı
├── curriculum/          # Ders içerikleri
└── tests/               # Test dosyaları
```

## 🔒 Güvenlik

Kullanıcı kodu şu korumalarla çalıştırılır:

- ✅ **İşlem İzolasyonu** - Ayrı process'te çalışır
- ✅ **Bellek Limiti** - Maksimum 100 MB
- ✅ **CPU Limiti** - Maksimum 5 saniye
- ✅ **Döngü Limiti** - Maksimum 2 milyon işlem
- ✅ **Modül Kısıtlaması** - Sadece güvenli modüller

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Katkı

Katkıda bulunmak için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını okuyun.
