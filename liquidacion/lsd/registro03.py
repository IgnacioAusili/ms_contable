from dataclasses import dataclass
from typing import ClassVar
from enum import StrEnum
from datetime import date
from decimal import Decimal

from core.validators import validar_cuil
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


class Unidad(StrEnum):
    """
    $=moneda; %=porcentuales; A=año; Q=quincena; M=mes; D=días; H=horas.
    Valor optativo, puede informarse en blanco.
    """
    MONEDA = "$"
    PORCENTAJE = "%"
    ANIO = "A"
    MES = "M"
    QUINCENA = "Q"
    DIAS = "D"
    HORAS = "H"


class DebitoCredito(StrEnum):
    DEBITO = "D"
    CREDITO = "C"


@dataclass
class DatosRegistro03:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "03"
    cuil_trabajador: str  # 11 enteros
    codigo_arca_concepto: str  # alfanumerico, longitud 10
    # Optativos
    cantidad: Decimal | None  # Longitud 5: 3 enteros y 2 decimales
    unidades: Unidad | None
    importe: Decimal | None  # Longitud 15: 13 enteros y 2 decimales
    debito_credito: DebitoCredito | None
    periodo_ajuste_retractivo: date | None  # formato AAAAMM
    """
    Para los conceptos liquidados del período informado en el registro 1, este valor se informa en 0. 
    Si hace referencia a una liquidación retroactiva del concepto, 
    se debe informar el periodo. Este dato es solo informativo
    """


class GeneradorRegistro03:
    """
    Detalle de los conceptos de sueldo liquidados a cada trabajador.
    """
    def __init__(self, datos: DatosRegistro03):
        self.datos = datos
        self.validador = ValidadorRegistro03(datos)
        self.formateador = FormateadorRegistro03(datos)

    def generar(self):
        self.validador.validar()

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuil_trabajador}"
            f"{self.formateador.codigo_arca_concepto_formateado()}"
            f"{self.formateador.cantidad_formateada()}"
            f"{self.formateador.unidades_formateada()}"
            f"{self.formateador.importe_formateado()}"
            f"{self.formateador.debito_credito_formateado()}"
            f"{self.formateador.periodo_ajuste_retractivo_formateado()}"
        )

        if len(resultado) == 51:
            return resultado
        else:
            raise Exception(
                "Error al generar Registro 03: longitud inválida.",
                len(resultado),
                resultado
            )


class FormateadorRegistro03:
    def __init__(self, datos: DatosRegistro03):
        self.datos = datos

    def codigo_arca_concepto_formateado(self):
        codigo_arca_concepto = self.datos.codigo_arca_concepto

        if codigo_arca_concepto:
            return f"{codigo_arca_concepto:<10}"
        else:
            return " " * 10

    def cantidad_formateada(self):
        cantidad = self.datos.cantidad

        if cantidad:
            cantidad = cantidad.quantize(Decimal("0.01"), rounding="ROUND_DOWN")
            return f"{cantidad:06}".replace(".", "")  # :06 considerando todavia el punto decimal
        else:
            return "0" * 5

    def unidades_formateada(self):
        unidades = self.datos.unidades

        if unidades:
            return unidades.value
        else:
            return " "

    def importe_formateado(self):
        importe = self.datos.importe

        if importe:
            importe = importe.quantize(Decimal("0.01"), rounding="ROUND_DOWN")
            return f"{importe:016}".replace(".", "")  # :016 considerando todavia el punnto decimal
        else:
            return "0" * 15

    def debito_credito_formateado(self):
        debito_credito = self.datos.debito_credito

        if debito_credito:
            return debito_credito.value
        else:
            return " "

    def periodo_ajuste_retractivo_formateado(self):
        periodo_ajuste_retractivo = self.datos.periodo_ajuste_retractivo

        if periodo_ajuste_retractivo:
            return periodo_ajuste_retractivo.strftime("%Y%m")
        else:
            return " " * 6


class ValidadorRegistro03:
    def __init__(self, datos: DatosRegistro03):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuil()
        self._validar_codigo_arca_concepto()
        self._validar_cantidad()
        self._validar_importe()

    def _validar_cuil(self):
        cuil = self.datos.cuil_trabajador

        if len(cuil) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIL de los trabajadores debe tener 11 dígitos."
            )

        validar_cuil(cuil)

    def _validar_codigo_arca_concepto(self):
        codigo_arca_concepto = self.datos.codigo_arca_concepto

        max_long = 10
        if len(codigo_arca_concepto) > max_long:
            raise Exception(
                f"El codigo del concepto no debe tener una longitud mayor a {max_long} digitos."
            )

    def _validar_cantidad(self):
        cantidad = self.datos.cantidad

        if not cantidad:
            return

        if not 0 <= cantidad < 1000:
            raise Exception(
                "La cantidad no es valida. Debe contener, como máximo, 3 digitos para la parte entera y 2 decimales."
            )

    def _validar_importe(self):
        importe = self.datos.importe

        if not importe:
            return

        if not 0 <= importe < 10000000000000:
            raise Exception(
                "El importe no es valido. Debe contener, como máximo, 13 digitos para la parte entera y 2 decimales."
            )
