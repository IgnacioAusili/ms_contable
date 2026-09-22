from django.db import models, transaction
from django.db.models import OuterRef, Subquery
from django.core.validators import MinValueValidator, RegexValidator

from concepto.utils import normalizar_identificador


class ConceptoQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(eliminado=False)

    def eliminados(self):
        return self.filter(eliminado=True)

    def delete(self):
        self.update(eliminado=True)

    @transaction.atomic
    def hard_delete(self):
        for concepto in self:
            VersionConcepto.todos.filter(concepto=concepto).delete()

        return super().delete()


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

    def delete(self, using=None, keep_parents=False):
        self.eliminado = True
        self.save(
            using=using,
            update_fields=["eliminado"],
        )

    @transaction.atomic
    def hard_delete(self):
        VersionConcepto.todos.filter(concepto=self).delete()
        return super().delete()

    def __str__(self):
        return f"Concepto {self.pk}"


class VersionConceptoQuerySet(models.QuerySet):
    def activos(self):
        return self.filter(concepto__eliminado=False)

    def eliminados(self):
        return self.filter(concepto__eliminado=True)

    def ultima_version(self):
        ultima_version = (
            VersionConcepto.todos
            .filter(concepto=OuterRef("concepto"))
            .order_by("-version")
            .values("pk")[:1]
        )

        return self.filter(pk=Subquery(ultima_version))


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

        @property
        def descripcion(self):
            return {
                self.CANTIDAD: "Numeros enteros.",
                self.PORCENTAJE: "Numeros reales del 0 al 100.",
            }[self]

        @property
        def constraint(self):
            return {
                self.CANTIDAD: lambda valor: valor == int(valor),
                self.PORCENTAJE: lambda valor: 0 <= valor <= 100,
            }[self]

        @property
        def sufijo(self):
            return {
                self.CANTIDAD: "",
                self.PORCENTAJE: "%",
            }[self]

        def calcular_importe(self, unidades, base):
            if self == self.CANTIDAD:
                return base * unidades
            if self == self.PORCENTAJE:
                return base * unidades / 100

            raise ValueError(f"Unidad no soportada: {self}")

    id = models.BigAutoField(
        primary_key=True,
    )

    concepto = models.ForeignKey(
        "concepto.Concepto",
        on_delete=models.DO_NOTHING,  # soft delete
        related_name="versiones",
    )

    grupo = models.ForeignKey(
        "grupo_concepto.GrupoConcepto",
        on_delete=models.PROTECT,
        related_name="versiones_concepto",
        null=True,
        blank=True,
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

    # ARCA define el Código de concepto de sueldo ARCA como un campo alfanumérico de longitud 6
    codigo_arca = models.CharField(
        max_length=6,
        null=False,
        blank=False,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]{6}$",
                message="El código ARCA debe contener exactamente 6 caracteres alfanuméricos.",
            ),
        ],
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

    @property
    def identificador(self):
        return f"{normalizar_identificador(self.denominacion)}_{self.id}"

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
