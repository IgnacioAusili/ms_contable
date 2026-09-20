from django.db import models


# Validar que si la liquidacion esta cerrada, este detalle tampoco se pueda modificar
class DetalleLiquidacion(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    liquidacion_empleado = models.ForeignKey(
        "liquidacion_empleado.LiquidacionEmpleado",
        on_delete=models.PROTECT,
        related_name="detalles",
    )

    concepto = models.ForeignKey(
        "version_concepto.VersionConcepto",
        on_delete=models.PROTECT,
        related_name="detalles_liquidacion",
    )

    unidades = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
    )

    base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False,
        help_text="Unidades * Base",
    )

    class Meta:
        verbose_name = "detalle liquidación"
        verbose_name_plural = "detalles de liquidación"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = type(self).objects.get(pk=self.pk)

            if self.liquidacion_empleado_id != original.liquidacion_empleado_id:
                raise ValueError(
                    "No se puede cambiar la liquidación asociada."
                )

            if self.concepto_id != original.concepto_id:
                raise ValueError(
                    "No se puede cambiar el concepto asociado."
                )

        self.importe = self.unidades * self.base
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.liquidacion_empleado.liquidacion.periodo} - {self.liquidacion_empleado.empleado.apellidos}, {self.liquidacion_empleado.empleado.nombres} - {self.concepto.denominacion}"
