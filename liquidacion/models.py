from django.db import models


class Liquidacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        CERRADA = "cerrada", "Cerrada"

    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="liquidaciones",
    )

    # Validar que el dia sea siempre el 1ro del mes p liquidaciones mensuales?
    # Agregar campo para definir si la liquidacion es mensual, quincenal, semanal, etc? Por ahora se asume que son mensuales
    periodo = models.DateField(
        null=False,
        blank=False,
    )

    fecha_pago = models.DateField(
        null=False,
        blank=False,
    )

    estado = models.CharField(
        max_length=30,
        choices=Estado.choices,
        null=False,
        blank=False,
    )

    domicilio_empresa = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
        help_text="Domicilio de la empresa al momento de realizar la liquidación.",
    )

    class Meta:
        verbose_name = "liquidación"
        verbose_name_plural = "liquidaciones"

        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "periodo"],
                name="unique_liquidacion_por_empresa_periodo",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.domicilio_empresa = self.empresa.domicilio
        else:
            original = type(self).objects.get(pk=self.pk)

            if self.empresa_id != original.empresa_id:
                raise ValueError(
                    "La empresa de una liquidación no puede ser modificada."
                )

            if original.estado == self.Estado.CERRADA:
                raise ValueError(
                    "Una liquidación cerrada no puede ser modificada."
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.periodo:%Y-%m} - {self.empresa}"
