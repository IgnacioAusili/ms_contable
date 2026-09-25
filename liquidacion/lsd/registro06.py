from dataclasses import dataclass
from typing import ClassVar
from enum import IntEnum
from decimal import Decimal

from core.validators import validar_cuil
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


@dataclass
class DatosRegistro06:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "06"
    # id_liquidacion: str  # Longitud 15 - Omitido. Ver docs/specs_externas/txt_lsd.md#Observación sobre Registro 06
    cuil_trabajador: str  # 11 enteros
    observaciones: str  # Longitud 80


class GeneradorRegistro06:
    """
    Campo de Observaciones: Es un campo opcional a completar con información que resulte útil para el empleador.
    """
    def __init__(self, datos: DatosRegistro06):
        self.datos = datos
        self.validador = ValidadorRegistro06(datos)
        self.formateador = FormateadorRegistro06(datos)

    def generar(self):
        self.validador.validar()

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuil_trabajador}"
            f"{self.formateador.observaciones_formateadas()}"
        )

        if len(resultado) == 93:  # 108 si se incluye id_liquidacion
            return resultado
        else:
            raise Exception(
                f"Error al generar Registro 06: longitud inválida.",
                len(resultado),
                resultado
            )


class FormateadorRegistro06:
    def __init__(self, datos: DatosRegistro06):
        self.datos = datos

    def observaciones_formateadas(self):
        observaciones = self.datos.observaciones

        if observaciones:
            return f"{observaciones:0>80}"
        else:
            return "0" * 80


class ValidadorRegistro06:
    def __init__(self, datos: DatosRegistro06):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuil()
        # self._validar_id_liquidacion()
        self._validar_observaciones()

    def _validar_cuil(self):
        cuil = self.datos.cuil_trabajador

        if len(cuil) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIL de los trabajadores debe tener 11 dígitos."
            )

        validar_cuil(cuil)

    # def _validar_id_liquidacion(self):
    #     id_liquidacion = self.datos.id_liquidacion
    #
    #     max_long = 15
    #     if len(id_liquidacion) > max_long:
    #         raise Exception(
    #             f"El id de liquidacion no debe tener una longitud mayor a {max_long} digitos."
    #         )
    #
    #     try:
    #         int(id_liquidacion)
    #     except ValueError:
    #         raise Exception(
    #             "El id de liquidacion debe ser numerico."
    #         )

    def _validar_observaciones(self):
        observaciones = self.datos.observaciones

        if observaciones == "":
            raise Exception(
                f"El campo observaciones es obligatorio."
            )

        max_long = 80
        if len(observaciones) > max_long:
            raise Exception(
                f"Las observaciones no deben tener una longitud mayor a {max_long} digitos."
            )
