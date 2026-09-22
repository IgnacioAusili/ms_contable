from django.db import models

from concepto.utils import normalizar_identificador


class GrupoConcepto(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    denominacion = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        help_text="Ej: Seguridad Social, INSSJP, Obra Social, etc",
    )

    @property
    def identificador(self):
        return f"{normalizar_identificador(self.denominacion).lower()}"

    class Meta:
        verbose_name = "grupo para conceptos"
        verbose_name_plural = "grupos para los conceptos"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = type(self).objects.get(pk=self.pk)

            if self.denominacion != original.denominacion:
                raise ValueError(
                    "La denominación de un grupo de concepto es inmutable."
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.denominacion
