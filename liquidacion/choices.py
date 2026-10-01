from django.db import models


class TipoEnvio(models.TextChoices):
    """
    'SJ': informa la liquidacion de SyJ y datos de la DJ F931.
    'RE': solo informa DJ F931 para casos donde se debe rectificar.
    """
    SJ = "SJ", "SJ (Informar Liquidación)"
    RE = "RE", "RE (Rectificar DJ F931)"


class TipoLiquidacion(models.TextChoices):
    """
    Si tipo_envio='SJ', los valores permitidos son mes='M' o quincena='Q', dias='D', horas='H'
    Si tipo_envio='RE', queda en blanco
    Este dato es solo informativo
    """
    M = "M", "Mes"
    Q = "Q", "Quincena"
    D = "D", "Días"
    H = "H", "Horas"


class UnidadesLsd(models.TextChoices):
    """
    $=moneda; %=porcentuales; A=año; Q=quincena; M=mes; D=días; H=horas.
    Valor optativo, puede informarse en blanco.
    """
    MONEDA = "$", "Moneda"
    PORCENTAJE = "%", "Porcentaje"
    A = "A", "Año"
    M = "M", "Mes"
    Q = "Q", "Quincena"
    D = "D", "Días"
    H = "H", "Horas"


class DebitoCredito(models.TextChoices):
    DEBITO = "D", "Débito"
    CREDITO = "C", "Crédito"
