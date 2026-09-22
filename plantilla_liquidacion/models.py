from django.db import models
from django.core.exceptions import ValidationError


class PlantillaLiquidacion(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.CASCADE,
        related_name="plantillas_liquidacion",
    )

    denominacion = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Plantilla para liquidacion"
        verbose_name_plural = "Plantillas para liquidacion"

        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "denominacion"],
                name="unique_plantilla_por_empresa",
            ),
        ]

    def __str__(self):
        return f"{self.denominacion}"


class DetallePlantillaLiquidacion(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    plantilla = models.ForeignKey(
        "plantilla_liquidacion.PlantillaLiquidacion",
        on_delete=models.CASCADE,
        related_name="detalles",
    )

    concepto = models.ForeignKey(
        "concepto.VersionConcepto",
        on_delete=models.PROTECT,
        related_name="detalles_plantillas",
    )

    unidades = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
    )

    formula_base = models.CharField(
        max_length=500,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Detalle de plantilla para liquidacion"
        verbose_name_plural = "Detalles de plantilla para liquidacion"

    def clean(self):
        super().clean()

        if (
            self.plantilla_id
            and self.concepto_id
            and self.plantilla.empresa_id != self.concepto.concepto.empresa_id
        ):
            raise ValidationError(
                "El concepto asociado no pertenece a la empresa de la plantilla."
            )

    def __str__(self):
        return f"identificador: {self.concepto.identificador}"
