# 🐍 Python Kurs Simulatörü

Terminal tabanlı, interaktif Python öğrenme platformu.

## ✨ Özellikler

- 🎓 **78+ Ders** - 16 bölüm boyunca kapsamlı Python müfredatı
- 🔒 **Güvenli Sandbox** - Kullanıcı kodu izole çalışır
- 🎨 **Syntax Highlighting** - Gerçek zamanlı renklendirme
- 📊 **İlerleme Takibi** - Tamamlanan ve atlanan görevler kaydedilir
- 🌈 **Türkçe Arayüz** - Tamamen Türkçe kullanıcı deneyimi

## 📦 Kurulum

### Gereksinimler

- Python 3.13+
- Terminal (curses destekli)

### Başlatma

```bash
# Projeyi klonla
git clone <repo-url>
cd "Python Kurs Simulatörü"

# Çalıştır
python3 main.py
```

> **Windows Kullanıcıları:** Program otomatik olarak `windows-curses` paketini yükleyecektir.

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
│  🐍 Python Kurs Simulatörü          │
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
