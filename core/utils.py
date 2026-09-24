import re


def format_decimal_2(value):
    if value is None:
        return ""
    return f"{value:.2f}"

def format_cuil(cuil):
    digitos = re.sub(r"\D", "", cuil)

    if len(digitos) != 11:
        raise ValueError("El CUIL debe contener 11 dígitos.")

    return f"{digitos[:2]}-{digitos[2:10]}-{digitos[10]}"
