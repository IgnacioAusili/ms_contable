from django.core.exceptions import ValidationError


def validar_no_remuneracion(denominacion):
    if denominacion.strip().lower() == "remuneracion":
        raise ValidationError(
            'La denominación no puede ser "remuneracion".'
        )
