from dataclasses import dataclass
from typing import ClassVar
from enum import StrEnum
from datetime import date
from core.validators import validar_cuil, validar_cbu
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


class FormaPago(StrEnum):
    EFECTIVO = "1"
    CHEQUE = "2"
    ACREDITACION_EN_CUENTA = "3"
    PAGO_EXTERNO = "4"


@dataclass
class DatosRegistro02:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "02"
    cuil_trabajador: str  # 11 enteros
    fecha_pago: date  # numerico, formato AAAAMMDD
    forma_pago: FormaPago
    # Optativos
    legajo_trabajador: str | None  # alfanumerico, longitud 10
    dependencia_revista_trabajador: str | None  # alfanumerico, longitud 50
    cbu_acreditacion_pago: str | None  # alfanumerico, longitud 22 - obligatorio cuando se indica Forma de pago = 3
    cantidad_dias_tope: int | None  # 3 enterios
    fecha_rubrica: date | None  # numerico, formato AAAAMMDD


class GeneradorRegistro02:
    """
    Datos generales de la liquidación de sueldo de cada trabajador.
    """
    def __init__(self, datos: DatosRegistro02):
        self.datos = datos
        self.validador = ValidadorRegistro02(datos)
        self.formateador = FormateadorRegistro02(datos)

    def generar(self):
        self.validador.validar()

        fecha_pago = self.datos.fecha_pago.strftime("%Y%m%d")

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuil_trabajador}"
            f"{self.formateador.legajo_formateado()}"
            f"{self.formateador.dependencia_revista_trabajador_formateado()}"
            f"{self.formateador.cbu_acreditacion_pago_formateado()}"
            f"{self.formateador.cantidad_dias_tope_formateada()}"
            f"{fecha_pago}"
            f"{self.formateador.fecha_rubrica_formateada()}"
            f"{self.datos.forma_pago.value}"
        )

        if len(resultado) == 115:
            return resultado
        else:
            raise Exception(
                "Error al generar Registro 02: longitud inválida.",
                len(resultado),
            )


class FormateadorRegistro02:
    def __init__(self, datos: DatosRegistro02):
        self.datos = datos

    def legajo_formateado(self):
        legajo = self.datos.legajo_trabajador

        if legajo:
            return f"{legajo:0>10}"
        else:
            return "0" * 10

    def dependencia_revista_trabajador_formateado(self):
        dependencia_revista_trabajador = self.datos.dependencia_revista_trabajador

        if dependencia_revista_trabajador:
            return f"{dependencia_revista_trabajador:<50}"
        else:
            return " " * 50

    def cbu_acreditacion_pago_formateado(self):
        cbu_acreditacion_pago = self.datos.cbu_acreditacion_pago

        if not cbu_acreditacion_pago:
            return " " * 22

        return cbu_acreditacion_pago

    def cantidad_dias_tope_formateada(self):
        cantidad_dias_tope = self.datos.cantidad_dias_tope

        if cantidad_dias_tope:
            return f"{cantidad_dias_tope:03d}"
        else:
            return "0" * 3

    def fecha_rubrica_formateada(self):
        fecha_rubrica = self.datos.fecha_rubrica

        if fecha_rubrica:
            return fecha_rubrica.strftime("%Y%m%d")
        else:
            return " " * 8


class ValidadorRegistro02:
    def __init__(self, datos: DatosRegistro02):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuil()
        self._validar_legajo()
        self._validar_dependencia_revista()
        self._validar_cbu()
        self._validar_cantidad_dias_tope()

    def _validar_cuil(self):
        cuil = self.datos.cuil_trabajador

        if len(cuil) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIL de los trabajadores debe tener 11 dígitos."
            )

        validar_cuil(cuil)

    def _validar_legajo(self):
        legajo = self.datos.legajo_trabajador

        if not legajo:
            return

        max_long = 10
        if len(legajo) > max_long:
            raise Exception(
                f"El legajo de los trabajadores no debe tener una longitud mayor a {max_long} digitos."
            )

    def _validar_dependencia_revista(self):
        dependencia_revista = self.datos.dependencia_revista_trabajador

        if not dependencia_revista:
            return

        max_long = 50
        if len(dependencia_revista) > max_long:
            raise Exception(
                f"La dependencia de revista de los trabajadores no debe "
                f"tener una longitud mayor a {max_long} digitos."
            )

    def _validar_cbu(self):
        cbu = self.datos.cbu_acreditacion_pago

        if not cbu:
            if self.datos.forma_pago == FormaPago.ACREDITACION_EN_CUENTA:
                raise Exception("El CBU es obligatorio para la forma de pago \"Acreditación en Cuenta\".")
            else:
                return

        if not cbu.isdigit():
            raise Exception("El CBU debe contener únicamente dígitos.")

        if len(cbu) != 22:
            raise Exception("El CBU debe tener 22 dígitos.")

        if not validar_cbu(cbu):
            raise Exception("El CBU es invalido.")

    def _validar_cantidad_dias_tope(self):
        cantidad_dias_tope = self.datos.cantidad_dias_tope

        if not cantidad_dias_tope:
            return

        if not 0 <= cantidad_dias_tope <= 999:
            raise Exception(
                "La cantidad de dias tope no es valida. Debe contener, como máximo, 3 digitos."
            )
