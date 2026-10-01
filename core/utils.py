import re
import unicodedata


def normalizar_identificador(texto):
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = texto.lower()
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("_")

    return texto


def format_decimal_2(value):
    if value is None:
        return ""
    return f"{value:.2f}"


def format_cuil(cuil):
    digitos = re.sub(r"\D", "", cuil)

    if len(digitos) != 11:
        raise ValueError("El CUIL debe contener 11 dígitos.")

    return f"{digitos[:2]}-{digitos[2:10]}-{digitos[10]}"
