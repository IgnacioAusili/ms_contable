from django.db import models


# Validar que si la liquidacion esta cerrada, esta por empleado tampoco se pueda modificar
class LiquidacionEmpleado(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    liquidacion = models.ForeignKey(
        "liquidacion.Liquidacion",
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    # Mostrar solo los de la empresa correspondiente
    empleado = models.ForeignKey(
        "empleado.Empleado",
        on_delete=models.PROTECT,
        related_name="liquidaciones",
    )

    # --- Calcular automaticamente al cerrar la liquidacion ---
    remunerativo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    no_remunerativo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    bruto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    descuentos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    neto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    contribuciones = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )

    costo_laboral = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        null=False,
        blank=False,
        editable=False,
    )
    # ------

    categoria = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        editable=False,
    )

    banco_de_cobro = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        verbose_name = "liquidación por empleado"
        verbose_name_plural = "liquidación por empleado"

        constraints = [
            models.UniqueConstraint(
                fields=["liquidacion", "empleado"],
                name="unique_empleado_por_liquidacion",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.categoria = self.empleado.categoria_laboral.denominacion
            self.banco_de_cobro = self.empleado.banco_de_cobro
        else:
            original = type(self).objects.get(pk=self.pk)

            if self.liquidacion_id != original.liquidacion_id:
                raise ValueError(
                    "La liquidación asociada no se puede modificar."
                )

            if self.empleado_id != original.empleado_id:
                raise ValueError(
                    "El empleado de una liquidación no puede ser modificado."
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.liquidacion.periodo} - {self.empleado.apellidos}, {self.empleado.nombres}"
