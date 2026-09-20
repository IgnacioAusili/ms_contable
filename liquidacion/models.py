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


# Validar que si la liquidacion esta cerrada, este detalle tampoco se pueda modificar
class DetalleLiquidacion(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    liquidacion_empleado = models.ForeignKey(
        "liquidacion.LiquidacionEmpleado",
        on_delete=models.PROTECT,
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

    expresion_base = models.CharField(
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

        # self.base = ...expresion_base
        # self.importe = self.unidades * self.base
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.liquidacion_empleado.liquidacion.periodo} - {self.liquidacion_empleado.empleado.apellidos}, {self.liquidacion_empleado.empleado.nombres} - {self.concepto.denominacion}"


# Falta control para evitar ciclos indirectos
# Evaluar expresion base: resolver referencias, validar el input, eval(detalle.expresion_base)
# Al resolver referencias, estas deben estar calculadas o calcularse
# Al cambiar un registro DETALLE_LIQUIDACION, hay que chequear las referencias y ajustar todos los valores
# ---
# 1. Resolver y calcular
#    - Resolver referencias
#    - Detectar ciclos indirectos
#    - Si una referencia no está calculada, calcularla primero
#    - Validar la expresión
#    - Evaluar expresion_base - eval(detalle.expresion_base)
#    - Calcular importe = unidades * base

# 2. Mantener consistencia
#    - Al modificar unidades, expresión o referencias de un detalle,
#      recalcular ese detalle y todos sus dependientes.
#    - Al modificar un detalle que es referenciado por otros,
#      recalcular todos los detalles afectados transitivamente.

# 3. Validaciones
#    - Referencias existentes
#    - Placeholders válidos
#    - Cada placeholder tiene una referencia correspondiente
#    - No existen ciclos directos ni indirectos
#    - Expresión contiene únicamente elementos permitidos
class ReferenciaDetalle(models.Model):
    detalle_origen = models.ForeignKey(
        DetalleLiquidacion,
        on_delete=models.CASCADE,
        related_name="referencias",
    )

    detalle_referenciado = models.ForeignKey(
        DetalleLiquidacion,
        on_delete=models.PROTECT,
        related_name="referenciado_por",
    )

    identificador = models.CharField(
        max_length=20,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "detalle_origen",
                    "identificador",
                ],
                name="unique_referencia_por_detalle",
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    detalle_origen=models.F("detalle_referenciado")
                ),
                name="referencia_no_autoreferente",
            )
        ]
