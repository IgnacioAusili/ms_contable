from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TramoSituacionRevista(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    dia_inicio = models.PositiveIntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )

    liquidacion_empleado = models.ForeignKey(
        "liquidacion.LiquidacionEmpleado",
        on_delete=models.PROTECT,
        related_name="situaciones_revista",
    )

    class Meta:
        verbose_name = "tramo de situacion de revista"
        verbose_name_plural = "tramos de situacion de revista"

    def __str__(self):
        return f"Situación de Revista"
