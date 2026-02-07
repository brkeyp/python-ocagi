def buyuk_harf(func):
    def wrapper():
        return func().upper()
    return wrapper

@buyuk_harf
def selamla():
    return 'merhaba'
