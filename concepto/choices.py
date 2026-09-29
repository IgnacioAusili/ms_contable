from django.db import models
from decimal import Decimal


class Categoria(models.TextChoices):
    TRABAJADOR = "trabajador", "Trabajador"
    EMPLEADOR = "empleador", "Empleador"


class Tipo(models.TextChoices):
    REMUNERATIVO = "remunerativo", "Remunerativo"
    NO_REMUNERATIVO = "no_remunerativo", "No remunerativo"
    DESCUENTO = "descuento", "Descuento"
    CONTRIBUCION = "contribucion", "Contribución"


class Unidad(models.TextChoices):
    CANTIDAD = "cantidad", "Cantidad"
    PORCENTAJE = "porcentaje", "Porcentaje"

    @property
    def descripcion(self):
        return {
            self.CANTIDAD: "Numeros reales.",
            self.PORCENTAJE: "Numeros reales del 0 al 100.",
        }[self]

    @property
    def constraint(self):
        return {
            self.CANTIDAD: lambda valor: isinstance(valor, Decimal),
            self.PORCENTAJE: lambda valor: isinstance(valor, Decimal) and 0 <= valor <= 100,
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
