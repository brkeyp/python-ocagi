# 🤝 Katkıda Bulunma Rehberi

Python Ocağı'na katkıda bulunmak istediğiniz için teşekkürler!

## 🚀 Başlarken

1. Projeyi fork edin
2. Yeni bir branch oluşturun: `git checkout -b feature/yeni-ozellik`
3. Değişikliklerinizi yapın
4. Testleri çalıştırın: `python3 -m pytest tests/ -v`
5. Commit edin: `git commit -m "feat: yeni özellik eklendi"`
6. Push edin: `git push origin feature/yeni-ozellik`
7. Pull Request açın

## 📝 Commit Mesajları

Semantic commit formatını kullanın:

- `feat:` - Yeni özellik
- `fix:` - Hata düzeltmesi
- `docs:` - Dokümantasyon
- `refactor:` - Kod düzenlemesi
- `test:` - Test ekleme/düzeltme
- `chore:` - Genel bakım

## 🧪 Test Yazma

Tüm yeni özellikler için test yazın:

```python
def test_yeni_ozellik():
    """Yeni özelliğin doğru çalıştığını doğrula."""
    sonuc = yeni_fonksiyon()
    assert sonuc == beklenen_deger
```

## 📚 Yeni Ders Ekleme

1. `tools/scaffold_lesson.py` kullanın
2. `task.json`, `validation.py`, `solution.py` oluşturun
3. UUID'nin benzersiz olduğundan emin olun

## 🎨 Kod Stili

- PEP 8 kurallarına uyun
- Türkçe dosya adları kullanmayın
- Yorumlar İngilizce veya Türkçe olabilir
- Type hints tercih edilir

## ❓ Sorular

Issue açarak soru sorabilirsiniz.
