def validate(scope, output):
    # Old Validator ID: 29
    return scope["selamla"]() == "Merhaba Misafir" and scope["selamla"]("Ali") == "Merhaba Ali"