from django.db import models
from django.core.exceptions import ValidationError

from concepto.models import VersionConcepto


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

    # Decision deliberada: Esta fecha puede ser del futuro puesto que puede ser válido preparar una liquidación anticipadamente
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
        editable=False
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

    def clean(self):
        super().clean()

        if self.periodo.day != 1:
            raise ValidationError(
                "El periodo de liquidacion debe comenzar en el primer dia del rango."
            )

        if self.periodo and self.fecha_pago:
            if (self.fecha_pago.year != self.periodo.year
                or self.fecha_pago.month != self.periodo.month
            ):
                raise ValidationError({
                    "fecha_pago": (
                        "La fecha de pago debe estar dentro del período "
                        "de la liquidación."
                    )
                })

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.estado = self.Estado.BORRADOR
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

    # TODO - que quede read_only al cerrar la liquidacion
    observaciones = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        editable=True,
        default="",
        help_text="Observaciones que se reflejaran en el recibo de sueldo"
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

    def clean(self):
        super().clean()

        if (
            self.liquidacion_id
            and self.empleado_id
            and self.liquidacion.empresa_id != self.empleado.empresa_id
        ):
            raise ValidationError(
                "El empleado no pertenece a la empresa de la liquidación."
            )

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


# TODO - Validar que si la liquidacion esta cerrada, este detalle tampoco se pueda modificar
class DetalleLiquidacion(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    liquidacion_empleado = models.ForeignKey(
        "liquidacion.LiquidacionEmpleado",
        on_delete=models.CASCADE,
        related_name="detalles",
    )

    concepto = models.ForeignKey(
        "concepto.VersionConcepto",
        on_delete=models.PROTECT,
        related_name="detalles_liquidacion",
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

    base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        editable=False,
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        blank=False,
        default=0,
        editable=False,
        help_text="Unidades * Base",
    )

    class Meta:
        verbose_name = "detalle liquidación"
        verbose_name_plural = "detalles de liquidación"

        constraints = [
            models.UniqueConstraint(
                fields=["liquidacion_empleado", "concepto"],
                name="unique_concepto_por_liquidacion_empleado",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.liquidacion_empleado_id
            and self.concepto_id
            and self.liquidacion_empleado.liquidacion.empresa_id != self.concepto.concepto.empresa_id
        ):
            raise ValidationError(
                "El concepto asociado no pertenece a la empresa de la liquidación."
            )

        unidad = VersionConcepto.Unidad(self.concepto.unidad)
        if not unidad.constraint(self.unidades):
            raise ValidationError({
                "unidades": (
                    f"El valor no es válido para la unidad "
                    f"{self.concepto.get_unidad_display()}."
                )
            })

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

        super().save(*args, **kwargs)

    def __str__(self):
        return f"identificador: {self.concepto.identificador}"
