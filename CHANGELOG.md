# Değişiklik Günlüğü

Bu proje [Semantic Versioning](https://semver.org/lang/tr/) ilkelerine uymaktadır.

## [1.1.0] - 2026-02-07

### Eklenenler
- CHANGELOG.md dosyası oluşturuldu
- validate_curriculum.py geliştirildi (solution.py kontrolü, alan tamamlığı, klasör formatı)

### Değişenler
- developer_message.txt → dev_message.txt olarak yeniden adlandırıldı
- README.md ders sayısı düzeltildi (78 → 98)
- Proje yapısı yeniden düzenlendi:
  - `ui/` paketi oluşturuldu
  - `input/` paketi oluşturuldu
  - `sandbox/` paketi oluşturuldu
- pyproject.toml eklendi (modern Python standartları)
- Kullanıcı verileri artık `~/.python_ocagi/` dizininde saklanıyor

### Düzeltmeler
- Kullanıcı verisi lokasyonu standartlaştırıldı (platform-bağımsız)

## [1.0.0] - 2026-02-06

### İlk Sürüm
- 98 ders, 16 bölüm içeren kapsamlı Python müfredatı
- Güvenli sandbox ortamı (memory, CPU, operation limits)
- Curses tabanlı terminal UI
- İlerleme takibi ve kaydetme
- Syntax highlighting
- Türkçe arayüz
