from django.db import models
from django.core.validators import MinValueValidator


class ConceptoQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(eliminado=False)

    def eliminados(self):
        return self.filter(eliminado=True)


class ConceptoManager(models.Manager.from_queryset(ConceptoQuerySet)):
    def get_queryset(self):
        return super().get_queryset().activos()


class Concepto(models.Model):
    objects = ConceptoManager()
    todos = ConceptoQuerySet.as_manager()

    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="conceptos",
    )

    eliminado = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = type(self).objects.get(pk=self.pk)

            if self.empresa_id != original.empresa_id:
                raise ValueError(
                    "El concepto no se puede cambiar de empresa."
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Concepto {self.pk}"


class VersionConceptoQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(concepto__eliminado=False)

    def eliminados(self):
        return self.filter(concepto__eliminado=True)


class VersionConceptoManager(models.Manager.from_queryset(VersionConceptoQuerySet)):
    def get_queryset(self):
        return super().get_queryset().activos()


class VersionConcepto(models.Model):
    objects = VersionConceptoManager()
    todos = VersionConceptoQuerySet.as_manager()

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
    )

    codigo_arca = models.CharField(
        max_length=255,
        null=False,
        blank=False,
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
        ordering = ("-version",)

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
        return f"{self.denominacion}"
