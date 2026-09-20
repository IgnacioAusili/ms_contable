from django.db import models


class Concepto(models.Model):
    id = models.BigAutoField(
        primary_key=True,
    )

    empresa = models.ForeignKey(
        "empresa.Empresa",
        on_delete=models.PROTECT,
        related_name="conceptos",
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
