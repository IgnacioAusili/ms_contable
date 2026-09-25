from django.db import models
from core.validators import validar_cuit


class Empresa(models.Model):
    class TipoEmpleador(models.TextChoices):
        ADMINISTRACION_PUBLICA = "administracion_publica", "Administración Pública"
        D81401_ART2_INCB = "d81401_art2_incb", "Decreto 814/01; Artículo 2, inc B"
        SERVICIOS_EVENTUALES_ART2_INCB = "servicios_eventuales_art2_incb", "Servicios Eventuales; Art 2, inc B"
        D81401_ART2_INCA = "d81401_art2_inca", "Decreto 814/01; Artículo 2, inc A"
        SERVICIOS_EVENTUALES_ART2_INCA = "servicios_eventuales_art2_inca", "Servicios Eventuales; Art 2, inc A"
        ENSENIANZA_PRIVADA = "ensenianza_privada", "Enseñanza Privada"
        D121203_AFA_CLUBES = "d121203_afa_clubes", "Decreto 1212/03; Clubes AFA"

    id = models.BigAutoField(primary_key=True)

    cuit = models.CharField(
        max_length=11,
        null=False,
        blank=False,
        validators=[validar_cuit],
    )

    nombre = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    tipo_empleador = models.CharField(
        max_length=50,
        choices=TipoEmpleador.choices,
        null=False,
        blank=False
    )

    domicilio = models.CharField(
        max_length=255,
        null=False,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = type(self).objects.get(pk=self.pk)

            if self.cuit != original.cuit:
                raise ValueError("El CUIT de una empresa es inmutable.")

            if self.nombre != original.nombre:
                raise ValueError("El nombre de una empresa es inmutable.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.cuit})"
