from django.db import models
from django.core.validators import MaxValueValidator
from empleado.validators import validar_dni, validar_cuil
from django.core.exceptions import ValidationError
from django.utils import timezone


class Empleado(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    categoria_laboral = models.ForeignKey(
        "categoria_laboral.CategoriaLaboral",
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    dni = models.CharField(
        max_length=8,
        null=False,
        blank=False,
        validators=[validar_dni],
    )

    cuil = models.CharField(
        max_length=11,
        null=False,
        blank=False,
        validators=[validar_cuil],
    )

    apellidos = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    nombres = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    legajo = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )

    fecha_ingreso = models.DateField(
        null=False,
        blank=False,
        validators=[
            MaxValueValidator(
                timezone.localdate(),
                message="La fecha de ingreso no puede ser futura.",
            ),
        ],
    )

    banco_de_cobro = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Ej: Nacion, Bco. Pcia. BS AS, Santander, etc",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "legajo"],
                name="unique_legajo_por_empresa",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.empresa_id
            and self.categoria_laboral_id
            and self.empresa_id != self.categoria_laboral.empresa_id
        ):
            raise ValidationError(
                "La cateogoria laboral asociada no pertenece a la misma empresa que este empleado."
            )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = type(self).objects.get(pk=self.pk)

            if self.empresa_id != original.empresa_id:
                raise ValueError(
                    "El empleado no se puede cambiar de empresa."
                )

            immutable_fields = [
                "dni",
                "cuil",
                "apellidos",
                "nombres",
                "legajo",
                "fecha_ingreso",
            ]

            for field in immutable_fields:
                if getattr(self, field) != getattr(original, field):
                    raise ValueError(
                        f"El campo '{field}' de un empleado es inmutable."
                    )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
