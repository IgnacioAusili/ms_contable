from dataclasses import dataclass
from typing import ClassVar
from datetime import date
from core.validators import validar_cuit
from liquidacion.choices import TipoLiquidacion, TipoEnvio
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


@dataclass
class DatosRegistro01:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "01"
    DIAS_BASE: ClassVar[str] = "30"
    cuit_empleador: str  # 11 enteros
    tipo_envio: str
    periodo_liquidacion: date  # periodo de la liquidacion de SyJ o de la DJ. Se informa en formato AAAAMM
    """
    Si tipo_envio='SJ', es el numero de liquidacion de SyJ del empleador. De existir liquidaciones ya ingresadas para 
      el período, el número de liquidación debe ser mayor al número de las ya ingresadas.
    Si tipo_envio='RE', queda en blanco
    """
    cantidad_trabajadores: int  # cantidad de trabajadores informados en registro 04. Se informa en fomrato 6 enteros
    # Optativos
    numero_liquidacion: int | None
    tipo_liquidacion: str | None


class GeneradorRegistro01:
    """
    Datos referenciales de la liquidacion.
    """
    def __init__(self, datos: DatosRegistro01):
        self.datos = datos
        self.validador = ValidadorRegistro01(datos)
        self.formateador = FormateadorRegistro01(datos)

    def generar(self):
        self.validador.validar()

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuit_empleador}"
            f"{self.datos.tipo_envio}"
            f"{self.formateador.periodo_liquidacion_formateado()}"
            f"{self.formateador.tipo_liquidacion_formateado()}"
            f"{self.formateador.numero_liquidacion_formateado()}"
            f"{self.datos.DIAS_BASE}"
            f"{self.formateador.cantidad_trabajadores_formateada()}"
        )

        if len(resultado) == 35:
            return resultado
        else:
            raise Exception(
                "Error al generar Registro 01: longitud inválida.",
                len(resultado),
                resultado
            )


class FormateadorRegistro01:
    def __init__(self, datos: DatosRegistro01):
        self.datos = datos

    def periodo_liquidacion_formateado(self):
        return self.datos.periodo_liquidacion.strftime("%Y%m")

    def tipo_liquidacion_formateado(self):
        tipo_liquidacion = self.datos.tipo_liquidacion

        if tipo_liquidacion:
            return tipo_liquidacion
        else:
            return " "

    def numero_liquidacion_formateado(self):
        numero_liquidacion = self.datos.numero_liquidacion

        if numero_liquidacion:
            return f"{numero_liquidacion:05d}"
        else:
            return "0" * 5

    def cantidad_trabajadores_formateada(self):
        return f"{self.datos.cantidad_trabajadores:06d}"


class ValidadorRegistro01:
    def __init__(self, datos: DatosRegistro01):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuit()
        self._validar_tipos()
        self._validar_numero_liquidacion()
        self._validar_cantidad_trabajadores()

    def _validar_cuit(self):
        cuit = self.datos.cuit_empleador

        if len(cuit) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIT del empleador debe tener 11 dígitos."
            )

        validar_cuit(cuit)

    def _validar_tipos(self):
        tipo_envio = self.datos.tipo_envio
        tipo_liq = self.datos.tipo_liquidacion

        if tipo_envio not in TipoEnvio.values:
            raise Exception(
                f"El tipo de envío {tipo_envio} no es válido."
            )

        if tipo_envio == TipoEnvio.RE:
            if tipo_liq:
                raise Exception(
                    "El tipo de liquidación debe quedar vacío cuando el tipo de envío es RE."
                )
        elif tipo_envio == TipoEnvio.SJ:
            if not tipo_liq:
                raise Exception(
                    "El tipo de liquidación debe ser M o Q cuando el tipo de envío es SJ."
                )

            if tipo_liq not in TipoLiquidacion.values:
                raise Exception(
                    f"El tipo de liquidación {tipo_liq} no es válido."
                )

    def _validar_numero_liquidacion(self):
        tipo_envio = self.datos.tipo_envio
        numero_liq = self.datos.numero_liquidacion

        if tipo_envio == TipoEnvio.RE:
            if numero_liq and numero_liq != 0:
                raise Exception(
                    "El número de liquidación debe quedar vacío cuando el tipo de envío es RE."
                )

        elif tipo_envio == TipoEnvio.SJ:
            if numero_liq == "":
                raise Exception(
                    "El número de liquidación es obligatorio cuando el tipo de envío es SJ."
                )

    def _validar_cantidad_trabajadores(self):
        cantidad_trabajadores = self.datos.cantidad_trabajadores

        if not 0 <= cantidad_trabajadores <= 999999:
            raise Exception(
                "La cantidad de trabajadores no es valida."
            )
