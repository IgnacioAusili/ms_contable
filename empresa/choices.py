from django.db import models


class TipoEmpleador(models.TextChoices):
    ADMINISTRACION_PUBLICA = "0", "Administración Pública"
    D81401_ART2_INCB = "1", "Decreto 814/01; Artículo 2, inc B"
    SERVICIOS_EVENTUALES_ART2_INCB = "2", "Servicios Eventuales; Art 2, inc B"
    D81401_ART2_INCA = "4", "Decreto 814/01; Artículo 2, inc A"
    SERVICIOS_EVENTUALES_ART2_INCA = "5", "Servicios Eventuales; Art 2, inc A"
    ENSENIANZA_PRIVADA = "7", "Enseñanza Privada"
    D121203_AFA_CLUBES = "8", "Decreto 1212/03; Clubes AFA"
