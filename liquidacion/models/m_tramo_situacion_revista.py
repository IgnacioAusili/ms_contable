from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class TramoSituacionRevista(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    liquidacion_empleado = models.ForeignKey(
        "liquidacion.LiquidacionEmpleado",
        on_delete=models.CASCADE,
        related_name="situaciones_revista",
    )

    codigo_situacion = models.CharField(
        max_length=2,
        null=False,
        blank=True,
    )

    dia_inicio = models.PositiveIntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )

    class Meta:
        verbose_name = "tramo de situacion de revista"
        verbose_name_plural = "tramos de situacion de revista"

    def __str__(self):
        return f"Situación de Revista"
