import pytest
import validators

# --- Basic Values ---

def test_validate_1_hello():
    assert validators.validate_1({"mesaj": "Merhaba Dünya"}, "")
    assert not validators.validate_1({"mesaj": "Hi"}, "")

def test_validate_2_year():
    assert validators.validate_2({"yil": 2025}, "")
    assert not validators.validate_2({"yil": 2024}, "")
    assert not validators.validate_2({"yil": "2025"}, "")

def test_validate_3_pi():
    assert validators.validate_3({"pi_sayisi": 3.14}, "")
    assert not validators.validate_3({"pi_sayisi": 3.14159}, "")

def test_validate_4_bool():
    assert validators.validate_4({"hazir_mi": True}, "")
    assert not validators.validate_4({"hazir_mi": False}, "")

def test_validate_5_sum():
    assert validators.validate_5({"toplam": 35}, "")
    assert not validators.validate_5({"toplam": 30}, "")

def test_validate_6_mod():
    assert validators.validate_6({"kalan": 1}, "")
    assert not validators.validate_6({"kalan": 0}, "")

def test_validate_7_cube():
    assert validators.validate_7({"kup": 125}, "")
    assert not validators.validate_7({"kup": 25}, "")

def test_validate_8_result():
    assert validators.validate_8({"sonuc": 21}, "")

def test_validate_9_str():
    assert validators.validate_9({"tam_isim": "Python Kursu"}, "")

def test_validate_10_str_format():
    assert validators.validate_10({"kisi_bilgisi": "Yaşım: 25"}, "")

def test_validate_11_upper():
    assert validators.validate_11({"sehir_buyuk": "ISTANBUL"}, "")

def test_validate_12_slice():
    assert validators.validate_12({"ilk_uc": "ABC"}, "")

def test_validate_13_reverse():
    assert validators.validate_13({"ters_metin": "amle"}, "")

# --- Collections ---

def test_validate_14_list():
    assert validators.validate_14({"sayilar": [10, 20, 30]}, "")
    assert not validators.validate_14({"sayilar": [10, 20]}, "")

def test_validate_15_list_str():
    assert validators.validate_15({"renkler": ["Mavi", "Yesil"]}, "")

def test_validate_16_list_index():
    assert validators.validate_16({"ortadaki": "Armut"}, "")

def test_validate_17_list_mut():
    assert validators.validate_17({"liste": [1, 2, 3, 4]}, "")

def test_validate_18_dict():
    assert validators.validate_18({"kimlik": {'ad': 'Ali', 'yas': 30}}, "")

def test_validate_19_dict_access():
    assert validators.validate_19({"isim_degeri": "Ali"}, "")

def test_validate_20_nested():
    assert validators.validate_20({"kimlik": {"meslek": "Mühendis"}}, "")
    assert not validators.validate_20({"kimlik": {"meslek": "Doktor"}}, "")

# --- Logic ---

def test_validate_21_cond():
    assert validators.validate_21({"durum": "Geçti"}, "")

def test_validate_22_cond2():
    assert validators.validate_22({"sonuc": "Tek"}, "")

def test_validate_23_elif():
    assert validators.validate_23({"derece": "B"}, "")

def test_validate_24_loop_sum():
    assert validators.validate_24({"toplam": 15}, "")

def test_validate_25_while():
    assert validators.validate_25({"sayac": 0}, "")

def test_validate_26_output():
    # Checks specific strings in output
    assert validators.validate_26({}, "20\n40\n60\n")
    assert not validators.validate_26({}, "20\n40")

# --- Functions & Classes ---

def test_validate_27_func():
    def kare_al(x): return x*x
    assert validators.validate_27({"kare_al": kare_al}, "")
    assert not validators.validate_27({"kare_al": lambda x: x+1}, "")

def test_validate_28_func_args():
    def carp(a, b): return a*b
    assert validators.validate_28({"carp": carp}, "")

def test_validate_29_func_default():
    class MockSelam:
        def __call__(self, name="Misafir"):
            return f"Merhaba {name}"
    # Or just a func
    def selamla(isim="Misafir"): return f"Merhaba {isim}"
    assert validators.validate_29({"selamla": selamla}, "")

def test_validate_30_return():
    def ikiye_bol(x): return float(x)/2
    assert validators.validate_30({"ikiye_bol": ikiye_bol}, "")

def test_validate_31_module():
    import math
    assert validators.validate_31({"math": math, "karekok": 4.0}, "")

def test_validate_32_random():
    assert validators.validate_32({"random": object, "sansli_sayi": 50}, "")
    assert not validators.validate_32({"random": object, "sansli_sayi": 101}, "")

def test_validate_33_exception():
    assert validators.validate_33({"sonuc": "Hata"}, "")

def test_validate_34_class():
    class Araba: pass
    assert validators.validate_34({"Araba": Araba}, "")
    assert not validators.validate_34({"Araba": "Proje"}, "")

def test_validate_35_class_init():
    class Kedi:
        def __init__(self, isim): self.isim = isim
    assert validators.validate_35({"Kedi": Kedi}, "")

def test_validate_36_class_method():
    assert validators.validate_36({"ses": "Hav!"}, "")

def test_validate_37_list_comp():
    assert validators.validate_37({"kareler": [x*x for x in range(1,11)]}, "")

def test_get_validator():
    assert validators.get_validator(1) == validators.validate_1
    assert validators.get_validator(37) == validators.validate_37
