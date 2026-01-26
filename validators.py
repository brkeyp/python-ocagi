import types

def validate_1(scope, output):
    return scope.get("mesaj") == "Merhaba Dünya"

def validate_2(scope, output):
    return scope.get("yil") == 2025 and isinstance(scope["yil"], int)

def validate_3(scope, output):
    return scope.get("pi_sayisi") == 3.14 and isinstance(scope["pi_sayisi"], float)

def validate_4(scope, output):
    return scope.get("hazir_mi") is True

def validate_5(scope, output):
    return scope.get("toplam") == 35

def validate_6(scope, output):
    return scope.get("kalan") == 1

def validate_7(scope, output):
    return scope.get("kup") == 125

def validate_8(scope, output):
    return scope.get("sonuc") == 21

def validate_9(scope, output):
    return scope.get("tam_isim") == "Python Kursu"

def validate_10(scope, output):
    return scope.get("kisi_bilgisi") == "Yaşım: 25"

def validate_11(scope, output):
    return scope.get("sehir_buyuk") == "ISTANBUL"

def validate_12(scope, output):
    return scope.get("ilk_uc") == "ABC"

def validate_13(scope, output):
    return scope.get("ters_metin") == "amle"

def validate_14(scope, output):
    return scope.get("sayilar") == [10, 20, 30]

def validate_15(scope, output):
    return scope.get("renkler") == ["Mavi", "Yesil"]

def validate_16(scope, output):
    return scope.get("ortadaki") == "Armut"

def validate_17(scope, output):
    return scope.get("liste") == [1, 2, 3, 4]

def validate_18(scope, output):
    return scope.get("kimlik") == {'ad': 'Ali', 'yas': 30}

def validate_19(scope, output):
    return scope.get("isim_degeri") == "Ali"

def validate_20(scope, output):
    return scope.get("kimlik", {}).get("meslek") == "Mühendis"

def validate_21(scope, output):
    return scope.get("durum") == "Geçti"

def validate_22(scope, output):
    return scope.get("sonuc") == "Tek"

def validate_23(scope, output):
    return scope.get("derece") == "B"

def validate_24(scope, output):
    return scope.get("toplam") == 15

def validate_25(scope, output):
    return scope.get("sayac") == 0

def validate_26(scope, output):
    return "20" in output and "40" in output and "60" in output

def validate_27(scope, output):
    return isinstance(scope.get("kare_al"), types.FunctionType) and scope["kare_al"](5) == 25

def validate_28(scope, output):
    return scope["carp"](3, 4) == 12

def validate_29(scope, output):
    return scope["selamla"]() == "Merhaba Misafir" and scope["selamla"]("Ali") == "Merhaba Ali"

def validate_30(scope, output):
    return scope["ikiye_bol"](10) == 5.0

def validate_31(scope, output):
    return "math" in scope and scope.get("karekok") == 4.0

def validate_32(scope, output):
    return "random" in scope and 1 <= scope.get("sansli_sayi") <= 100

def validate_33(scope, output):
    return scope.get("sonuc") == "Hata"

def validate_34(scope, output):
    return isinstance(scope.get("Araba"), type)

def validate_35(scope, output):
    return scope["Kedi"]("Tekir").isim == "Tekir"

def validate_36(scope, output):
    return scope.get("ses") == "Hav!"

def validate_37(scope, output):
    return scope.get("kareler") == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

def get_validator(step_id):
    """
    ID'ye göre ilgili doğrulama fonksiyonunu döndürür.
    """
    validator_map = {
        1: validate_1,
        2: validate_2,
        3: validate_3,
        4: validate_4,
        5: validate_5,
        6: validate_6,
        7: validate_7,
        8: validate_8,
        9: validate_9,
        10: validate_10,
        11: validate_11,
        12: validate_12,
        13: validate_13,
        14: validate_14,
        15: validate_15,
        16: validate_16,
        17: validate_17,
        18: validate_18,
        19: validate_19,
        20: validate_20,
        21: validate_21,
        22: validate_22,
        23: validate_23,
        24: validate_24,
        25: validate_25,
        26: validate_26,
        27: validate_27,
        28: validate_28,
        29: validate_29,
        30: validate_30,
        31: validate_31,
        32: validate_32,
        33: validate_33,
        34: validate_34,
        35: validate_35,
        36: validate_36,
        37: validate_37,
    }
    return validator_map.get(step_id)
