from django.db import models


class Empleado(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    # Reglas de Negocio: la categoria_laboral tiene que pertenecer a la misma empresa que el empleado
    categoria_laboral = models.ForeignKey(
        "categoria_laboral.CategoriaLaboral",
        on_delete=models.PROTECT,
        related_name="empleados",
    )

    dni = models.CharField(
        max_length=8,
        null=False,
        blank=False,
    )

    cuil = models.CharField(
        max_length=11,
        null=False,
        blank=False,
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
    )

    banco_de_cobro = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        help_text="Ej: Nacion, Bco. Pcia. BS AS, Santander, etc",
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "legajo"],
                name="unique_legajo_por_empresa",
            ),
        ]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres}"
