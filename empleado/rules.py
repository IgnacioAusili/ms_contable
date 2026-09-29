from django.core.exceptions import ValidationError
from empleado.choices import FormaPago


def validar_dni_cuil(dni, cuil):
    if dni not in cuil:
        raise ValidationError({
            "cuil": "El CUIL no se corresponde con el DNI."
        })


def validar_forma_pago_cbu(forma_de_pago, cbu):
    try:
        forma_de_pago = int(forma_de_pago)
    except Exception:
        raise ValidationError({
            "forma_de_pago": (
                "La Forma de Pago es inválida."
            )
        })

    if forma_de_pago == FormaPago.ACREDITACION_EN_CUENTA:
        if not cbu or cbu == "":
            raise ValidationError({
                "cbu": (
                    "Si la forma de pago es Acreditación en Cuenta, debe especificar el CBU/CVU."
                )
            })
