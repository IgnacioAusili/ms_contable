from dataclasses import dataclass
from typing import ClassVar
from decimal import Decimal
from datetime import date
from core.validators import validar_cuil
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


@dataclass
class DatosRegistro05:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "05"
    cuil_trabajador: str  # 11 enteros
    categoria_profesional: str  # Longitud 6
    puesto_desempeniado: str  # Longitud 4
    fecha_ingreso: date  # Se informa en formato AAAAMMDD
    fecha_egreso: date  # Se informa en formato AAAAMMDD
    remuneracion: Decimal  # Longitud 15. 13 enteros, 2 decimales
    cuit_empleador: str  # 11 enteros


class GeneradorRegistro05:
    """
    información detallada de los trabajadores eventuales para la emisión del Libro Especial, Dec. 342/1992
    """
    def __init__(self, datos: DatosRegistro05):
        self.datos = datos
        self.validador = ValidadorRegistro05(datos)
        self.formateador = FormateadorRegistro05(datos)

    def generar(self):
        self.validador.validar()

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuil_trabajador}"
            f"{self.formateador.categoria_profesional_formateada()}"
            f"{self.formateador.puesto_desempeniado_formateado()}"
            f"{self.formateador.fecha_formateada(self.datos.fecha_ingreso)}"
            f"{self.formateador.fecha_formateada(self.datos.fecha_egreso)}"
            f"{self.formateador.remuneracion_formateada()}"
            f"{self.datos.cuit_empleador}"
        )

        if len(resultado) == 65:
            return resultado
        else:
            raise Exception(
                f"Error al generar Registro 05: longitud inválida.",
                len(resultado),
                resultado
            )


class FormateadorRegistro05:
    def __init__(self, datos: DatosRegistro05):
        self.datos = datos

    def categoria_profesional_formateada(self):
        categoria_profesional = self.datos.categoria_profesional

        if categoria_profesional:
            return f"{categoria_profesional:0>6}"
        else:
            return "0" * 6

    def puesto_desempeniado_formateado(self):
        puesto_desempeniado = self.datos.puesto_desempeniado

        if puesto_desempeniado:
            return f"{puesto_desempeniado:0>4}"
        else:
            return "0" * 4

    def fecha_formateada(self, fecha: date):
        if fecha:
            return fecha.strftime("%Y%m%d")
        else:
            return "0" * 8

    def remuneracion_formateada(self):
        remuneracion = self.datos.remuneracion

        if remuneracion:
            remuneracion = remuneracion.quantize(Decimal("0.01"), rounding="ROUND_DOWN")
            return f"{remuneracion:016}".replace(".", "")  # :016 considerando todavia el punnto decimal
        else:
            return "0" * 15


class ValidadorRegistro05:
    def __init__(self, datos: DatosRegistro05):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuil()
        self._validar_categoria_profesional()
        self._validar_puesto_desempeniado()
        self._validar_fechas()
        self._validar_remuneracion()

    def _validar_cuil(self):
        cuil_trab = self.datos.cuil_trabajador
        cuit_empl = self.datos.cuit_empleador

        if len(cuil_trab) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIL de los trabajadores debe tener 11 dígitos."
            )

        if len(cuit_empl) != 11:
            raise Exception(
                "El CUIT del empleador debe tener 11 dígitos."
            )

        validar_cuil(cuil_trab)
        validar_cuil(cuit_empl)

    def _validar_categoria_profesional(self):
        categoria_profesional = self.datos.categoria_profesional

        max_long = 6
        if len(categoria_profesional) > max_long:
            raise Exception(
                f"La categoría profesional no debe tener una longitud mayor a {max_long} digitos."
            )

    def _validar_puesto_desempeniado(self):
        puesto_desempeniado = self.datos.puesto_desempeniado

        max_long = 4
        if len(puesto_desempeniado) > max_long:
            raise Exception(
                f"El puesto desempeñado no debe tener una longitud mayor a {max_long} digitos."
            )

    def _validar_fechas(self):
        fecha_ingreso = self.datos.fecha_ingreso
        fecha_egreso = self.datos.fecha_egreso

        if fecha_egreso < fecha_ingreso:
            raise Exception(
                "La fecha de ingreso no puede ser posterior a la de egreso."
            )

    def _validar_remuneracion(self):
        remuneracion = self.datos.remuneracion

        if not remuneracion:
            return

        if not 0 <= remuneracion < 10000000000000:
            raise Exception(
                "La remuneracion no es valida. Debe contener, como máximo, 13 digitos para la parte entera y 2 decimales."
            )
