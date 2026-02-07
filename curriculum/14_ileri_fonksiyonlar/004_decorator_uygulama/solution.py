sayac = 0

def tekrarla(n):
    def decorator(func):
        def wrapper():
            global sayac
            for i in range(n):
                func()
                sayac = sayac + 1
        return wrapper
    return decorator

@tekrarla(3)
def merhaba():
    pass

merhaba()
