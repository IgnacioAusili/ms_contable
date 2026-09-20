from django.core.exceptions import ValidationError


def es_dni_valido(value):
    if value is None:
        return False

    value = str(value).strip()

    return value.isdigit() and 7 <= len(value) <= 8


def validar_dni(value):
    if not es_dni_valido(value):
        raise ValidationError(
            "El DNI debe contener entre 7 y 8 dígitos."
        )


def es_cuit_valido(value):
    return es_cuil_valido(value)


def validar_cuit(value):
    if not es_cuit_valido(value):
        raise ValidationError(
            "El CUIT no es válido."
        )


def es_cuil_valido(value):
    if value is None:
        return False

    value = str(value).strip()

    if len(value) != 11 or not value.isdigit():
        return False

    # Los primeros 10 dígitos se utilizan para calcular el dígito verificador.
    digitos = [int(d) for d in value]

    ponderadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    suma = sum(
        digito * ponderador
        for digito, ponderador in zip(digitos[:10], ponderadores)
    )

    resto = suma % 11
    digito_verificador = 11 - resto

    if digito_verificador == 11:
        digito_verificador = 0
    elif digito_verificador == 10:
        # El CUIL no es válido con esta combinación.
        return False

    return digito_verificador == digitos[10]


def validar_cuil(value):
    if not es_cuil_valido(value):
        raise ValidationError(
            "El CUIL no es válido."
        )
