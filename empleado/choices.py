from django.db import models


class FormaPago(models.IntegerChoices):
    EFECTIVO = 1, "Efectivo"
    CHEQUE = 2, "Cheque"
    ACREDITACION_EN_CUENTA = 3, "Acreditación en Cuenta"
    PAGO_EXTERNO = 4, "Pago Externo"
