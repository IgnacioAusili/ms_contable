from django.db import models
from django.core.exceptions import ValidationError


class Liquidacion(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        EN_RECTIFICACION = "en_rectificacion", "En Rectificación"
        CERRADA = "cerrada", "Cerrada"

    class TipoEnvio(models.TextChoices):
        SJ = "SJ", "SJ (Informar Liquidación)"
        RE = "RE", "RE (Rectificar DJ F931)"

    class TipoLiquidacion(models.TextChoices):
        M = "M", "Mes"
        Q = "Q", "Quincena"
        D = "D", "Días"
        H = "H", "Horas"

    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="liquidaciones",
    )

    # Decision deliberada: Esta fecha puede ser del futuro puesto que
    # puede ser válido preparar una liquidación anticipadamente
    periodo = models.DateField(
        null=False,
        blank=False,
    )

    numero = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        default=None,
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

    tipo_envio = models.CharField(
        max_length=10,
        choices=TipoEnvio.choices,
        null=False,
        blank=False,
    )

    tipo_liquidacion = models.CharField(
        max_length=10,
        choices=TipoLiquidacion.choices,
        null=False,
        blank=True,
    )

    observaciones = models.CharField(
        max_length=80,
        null=False,
        blank=True,
        help_text="Observaciones para Libro de Sueldos Digital de ARCA. Max 80 caracteres.",
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
                fields=["empresa", "periodo", "numero"],
                name="unique_liquidacion_por_empresa_periodo_numero",
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
                or self.fecha_pago.month not in (self.periodo.month, self.periodo.month+1)
            ):
                raise ValidationError({
                    "fecha_pago": (
                        "La fecha de pago debe estar dentro del período "
                        "de la liquidación, o del siguiente."
                    )
                })

        if self.tipo_envio == self.TipoEnvio.RE and self.tipo_liquidacion != "":
            raise ValidationError({
                "tipo_liquidacion": (
                    "El tipo de liquidación debe quedar vacio cuando el tipo de envío es 'RE'."
                )
            })

        if self.tipo_envio == self.TipoEnvio.RE and self.numero:
            raise ValidationError({
                "numero": (
                    "El numero de liquidacion no debe especificarse cuando el tipo de envío es 'RE'."
                )
            })

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.estado = self.Estado.BORRADOR
            self.domicilio_empresa = self.empresa.domicilio

            if self.tipo_envio == self.TipoEnvio.SJ:
                ultima = (
                    type(self).objects
                    .filter(
                        empresa=self.empresa,
                        periodo=self.periodo,
                        tipo_envio=self.TipoEnvio.SJ,
                    )
                    .order_by("-numero")
                    .first()
                )

                self.numero = (ultima.numero if ultima else 0) + 1
            else:
                self.numero = None
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
