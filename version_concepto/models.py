from django.db import models
from django.core.validators import MinValueValidator


class VersionConcepto(models.Model):
    class Categoria(models.TextChoices):
        TRABAJADOR = "trabajador", "Trabajador"
        EMPLEADOR = "empleador", "Empleador"

    class Tipo(models.TextChoices):
        REMUNERATIVO = "remunerativo", "Remunerativo"
        NO_REMUNERATIVO = "no_remunerativo", "No remunerativo"
        DESCUENTO = "descuento", "Descuento"
        REDONDEO = "redondeo", "Redondeo"
        CONTRIBUCION = "contribucion", "Contribución"

    class Unidad(models.TextChoices):
        CANTIDAD = "cantidad", "Cantidad"
        PORCENTAJE = "porcentaje", "Porcentaje"

    id = models.BigAutoField(
        primary_key=True,
    )

    concepto = models.ForeignKey(
        "concepto.Concepto",
        on_delete=models.PROTECT,
        related_name="versiones",
    )

    grupo = models.ForeignKey(
        "grupo_concepto.GrupoConcepto",
        on_delete=models.PROTECT,
        related_name="versiones_concepto",
    )

    version = models.PositiveIntegerField(
        null=False,
        blank=False,
        editable=False,
        validators=[MinValueValidator(1)],
    )

    denominacion = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Ej: Sueldo Basico, Obra Social, etc",
    )

    codigo_arca = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Referencia a un concepto de ARCA",
    )

    categoria = models.CharField(
        max_length=50,
        choices=Categoria.choices,
        null=False,
        blank=False,
    )

    tipo = models.CharField(
        max_length=50,
        choices=Tipo.choices,
        null=False,
        blank=False,
    )

    unidad = models.CharField(
        max_length=50,
        choices=Unidad.choices,
        null=False,
        blank=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["concepto", "version"],
                name="unique_version_por_concepto",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk is None:
            ultima_version = (
                type(self).objects
                .filter(concepto=self.concepto)
                .order_by("-version")
                .values_list("version", flat=True)
                .first()
            )

            self.version = (ultima_version or 0) + 1
        else:
            raise ValueError(
                "Esta entidad no es editable." # deshabilitar desde la UI. Solo si tiene asociado algun detalle de una liquidacion cerrada
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.denominacion} (v{self.version})"
