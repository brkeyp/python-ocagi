def validate(scope, output):
        return scope["selamla"]() == "Merhaba Misafir" and scope["selamla"]("Ali") == "Merhaba Ali"