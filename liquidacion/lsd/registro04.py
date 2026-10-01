from dataclasses import dataclass
from typing import ClassVar
from decimal import Decimal

from core.validators import validar_cuil
from empresa.choices import TipoEmpleador
from liquidacion.lsd.utils import validar_datos_obligatorios_dataclass


@dataclass
class DatosRegistro04:
    # Obligatorios
    TIPO_REGISTRO: ClassVar[str] = "04"
    CODIGO_TIPO_OPERACION: ClassVar[bool] = False
    cuil_trabajador: str  # 11 enteros
    tipo_empleador: str
    codigo_situacion_revista: str  # Longitud 2
    codigo_condicion: str  # Longitud 2
    codigo_actividad: str  # Longitud 3
    codigo_modalidad_contratacion: str  # Longitud 3
    codigo_siniestrado: str  # Longitud 2
    codigo_localidad: str  # Longitud 2
    codigo_obra_social: str  # Longitud 6
    remuneracion_bruta: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_1: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_2: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_3: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_4: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_5: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_6: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_7: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_8: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_9: Decimal  # Longitud 15. 13 enteros, 2 decimales
    base_imponible_10: Decimal  # Longitud 15. 13 enteros, 2 decimales
    detracciones: Decimal  # Longitud 15. 13 enteros, 2 decimales
    codigo_situacion_revista_1: str | None  # Longitud 2
    dia_inicio_situacion_revista_1: int | None  # Longitud 2
    conyuge: bool | None
    marca_cct: bool | None
    marca_scvo: bool | None
    marca_reduccion: bool | None
    # Optativos
    cantidad_hijos: int | None  # Longitud 2
    codigo_situacion_revista_2: str | None # Longitud 2
    dia_inicio_situacion_revista_2: int | None  # Longitud 2
    codigo_situacion_revista_3: str | None  # Longitud 2
    dia_inicio_situacion_revista_3: int | None  # Longitud 2
    cantidad_dias_trabajados: int | None  # Longitud 2. Excluyente con cantidad_horas_trabajadas
    cantidad_horas_trabajadas: int | None  # Longitud 3. Excluyente con cantidad_dias_trabajados
    porcentaje_aporte_adicional_seg_social: Decimal | None  # Longitud 5. 3 enteros, 2 decimales
    porcentaje_contrib_tarea_diferencial: Decimal | None  # Longitud 5. 3 enteros, 2 decimales
    cantidad_adherentes_obra_social: int | None  # Longitud 2
    aporte_adicional_obra_social: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    contrib_adicional_obra_social: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    base_calc_diferencial_aportes_obra_social_fsr: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    base_calc_diferencial_contrib_obra_social_fsr: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    base_calc_diferencial_ley_riesgos_trabajo: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    remuneracion_maternidad_anses: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    base_calc_diferencial_aportes_seg_social: Decimal | None  # Longitud 15. 13 enteros, 2 decimales
    base_calc_diferencial_contrib_seg_social: Decimal | None  # Longitud 15. 13 enteros, 2 decimales


class GeneradorRegistro04:
    """
    Atributos de la relación laboral de cada trabajador para la determinación de las deudas con el SUSS.
    """
    def __init__(self, datos: DatosRegistro04):
        self.datos = datos
        self.validador = ValidadorRegistro04(datos)
        self.formateador = FormateadorRegistro04(datos)

    def generar(self):
        self.validador.validar()

        resultado = (
            f"{self.datos.TIPO_REGISTRO}"
            f"{self.datos.cuil_trabajador}"
            f"{self.formateador.bools_formateados(self.datos.conyuge)}"
            f"{self.formateador.formateado_como_entero(self.datos.cantidad_hijos, 2)}"
            f"{self.formateador.bools_formateados(self.datos.marca_cct)}"
            f"{self.formateador.bools_formateados(self.datos.marca_scvo)}"
            f"{self.formateador.bools_formateados(self.datos.marca_reduccion)}"
            f"{self.datos.tipo_empleador}"
            f"{self.formateador.bools_formateados(self.datos.CODIGO_TIPO_OPERACION)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_situacion_revista, 2)}"
            f"{self.formateador.formateado_como_string(self.datos.codigo_condicion, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_actividad, 3)}"
            f"{self.formateador.formateado_como_string(self.datos.codigo_modalidad_contratacion, 3)}"
            f"{self.formateador.formateado_como_string(self.datos.codigo_siniestrado, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_localidad, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_situacion_revista_1, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.dia_inicio_situacion_revista_1, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_situacion_revista_2, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.dia_inicio_situacion_revista_2, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_situacion_revista_3, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.dia_inicio_situacion_revista_3, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.cantidad_dias_trabajados, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.cantidad_horas_trabajadas, 3)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.porcentaje_aporte_adicional_seg_social, 3, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.porcentaje_contrib_tarea_diferencial, 3, 2)}"
            f"{self.formateador.formateado_como_entero(self.datos.codigo_obra_social, 6)}"
            f"{self.formateador.formateado_como_entero(self.datos.cantidad_adherentes_obra_social, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.aporte_adicional_obra_social, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.contrib_adicional_obra_social, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_calc_diferencial_aportes_obra_social_fsr, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_calc_diferencial_contrib_obra_social_fsr, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_calc_diferencial_ley_riesgos_trabajo, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.remuneracion_maternidad_anses, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.remuneracion_bruta, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_1, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_2, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_3, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_4, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_5, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_6, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_7, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_8, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_9, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_calc_diferencial_aportes_seg_social, 13, 2)}"
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_calc_diferencial_contrib_seg_social, 13, 2)}"       
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.base_imponible_10, 13, 2)}"            
            f"{self.formateador.numeros_con_decimales_formateados(self.datos.detracciones, 13, 2)}"
        )

        if len(resultado) == 370:
            return resultado
        else:
            raise Exception(
                f"Error al generar Registro 04: longitud inválida.",
                len(resultado),
                resultado
            )


class FormateadorRegistro04:
    def __init__(self, datos: DatosRegistro04):
        self.datos = datos

    def bools_formateados(self, valor: bool | None):
        if valor:
            return "1"
        else:
            return "0"

    def numeros_con_decimales_formateados(self, valor: Decimal, long_entero: int, long_decimal: int):
        longitud_total = long_entero + long_decimal

        if valor:
            valor = valor.quantize(
                Decimal("1." + "0" * long_decimal),
                rounding="ROUND_DOWN",
            )

            return f"{valor:0{longitud_total+1}}".replace(".", "")
        else:
            return "0" * longitud_total

    def formateado_como_entero(self, valor, long: int):
        if valor:
            if isinstance(valor, str):
                return f"{valor:0>{long}}"

            return f"{valor:0{long}d}"
        else:
            return "0" * long

    def formateado_como_string(self, valor, long: int):
        if valor:
            if isinstance(valor, str):
                try:
                    valor = int(valor)
                except ValueError:
                    pass

            return f"{valor:<{long}}"
        else:
            return " " * long

class ValidadorRegistro04:
    def __init__(self, datos: DatosRegistro04):
        self.datos = datos

    def validar(self):
        validar_datos_obligatorios_dataclass(self.datos)
        self._validar_cuil()
        self._validar_tipo_empleador()
        self._validar_codigos_longitud()
        self._validar_numeros_decimales()
        self._validar_dia_inicio_situaciones_revista()
        self._validar_cantidad_hijos()
        self._validar_tiempo_trabajado()
        self._validar_cantidad_adherentes_obra_social()

    def _validar_cuil(self):
        cuil = self.datos.cuil_trabajador

        if len(cuil) != 11:
            raise Exception(  # TODO - definir mejor el tipo de excepcion
                "El CUIL de los trabajadores debe tener 11 dígitos."
            )

        validar_cuil(cuil)

    def _validar_tipo_empleador(self):
        tipo_empleador = self.datos.tipo_empleador

        if tipo_empleador not in TipoEmpleador.values:
            raise Exception(
                f"El tipo de empleador {tipo_empleador} no es válido."
            )

    def _validar_codigos_longitud(self):
        codigos = [
            ("Codigo de situacion de revista", self.datos.codigo_situacion_revista, True, 2),
            ("Codigo de condicion", self.datos.codigo_condicion, True, 2),
            ("Codigo de actividad", self.datos.codigo_actividad, True, 3),
            ("Codigo de modalidad de contratacion", self.datos.codigo_modalidad_contratacion, True, 3),
            ("Codigo de siniestrado", self.datos.codigo_siniestrado, True, 2),
            ("Codigo de localidad", self.datos.codigo_localidad, True, 2),
            ("Codigo de situacion de revista 1", self.datos.codigo_situacion_revista_1, False, 2),
            ("Codigo de obra social", self.datos.codigo_obra_social, True, 6),
            ("Codigo de situacion de revista 2", self.datos.codigo_situacion_revista_2, False, 2),
            ("Codigo de situacion de revista 3", self.datos.codigo_situacion_revista_3, False, 2),
        ]

        for nombre, valor, obligatorio, max_long in codigos:
            if not valor:
                if obligatorio:
                    raise Exception(
                        f"{nombre} es obligatorio."
                    )
                else:
                    continue

            if len(valor) > max_long:
                raise Exception(
                    f"{nombre} no debe tener una longitud mayor a {max_long} digitos."
                )

    def _validar_numeros_decimales(self):
        numeros_decimales = [
            ("Remuneracion bruta", self.datos.remuneracion_bruta, True, 13, 2),
            ("Base imponible 1", self.datos.base_imponible_1, True, 13, 2),
            ("Base imponible 2", self.datos.base_imponible_2, True, 13, 2),
            ("Base imponible 3", self.datos.base_imponible_3, True, 13, 2),
            ("Base imponible 4", self.datos.base_imponible_4, True, 13, 2),
            ("Base imponible 5", self.datos.base_imponible_5, True, 13, 2),
            ("Base imponible 6", self.datos.base_imponible_6, True, 13, 2),
            ("Base imponible 7", self.datos.base_imponible_7, True, 13, 2),
            ("Base imponible 8", self.datos.base_imponible_8, True, 13, 2),
            ("Base imponible 9", self.datos.base_imponible_9, True, 13, 2),
            ("Base imponible 10", self.datos.base_imponible_10, True, 13, 2),
            ("Detracciones", self.datos.detracciones, True, 13, 2),
            ("Porcentaje de aporte adicional de seguridad social",
             self.datos.porcentaje_aporte_adicional_seg_social, False, 3, 2),
            ("Porcentaje de contribucion por tarea diferencial",
             self.datos.porcentaje_contrib_tarea_diferencial, False, 3, 2),
            ("Aporte adicional de obra social",
             self.datos.aporte_adicional_obra_social, False, 13, 2),
            ("Contribucion adicional de obra social",
             self.datos.contrib_adicional_obra_social, False, 13, 2),
            ("Base para el calculo diferencial de aporte de obra social y FSR",
             self.datos.base_calc_diferencial_aportes_obra_social_fsr, False, 13, 2),
            ("Base para el calculo diferencial de contribucion de obra social y FSR",
             self.datos.base_calc_diferencial_contrib_obra_social_fsr, False, 13, 2),
            ("Base para el calculo diferencial Ley de Riesgos de Trabajo",
             self.datos.base_calc_diferencial_ley_riesgos_trabajo, False, 13, 2),
            ("Remuneracion por maternidad ANSeS",
             self.datos.remuneracion_maternidad_anses, False, 13, 2),
            ("Base para el calculo diferencial de aporte de seguridad social",
             self.datos.base_calc_diferencial_aportes_seg_social, False, 13, 2),
            ("Base para el calculo diferencial de contribucion de seguridad social",
             self.datos.base_calc_diferencial_contrib_seg_social, False, 13, 2),
        ]

        for nombre, valor, obligatorio, long_entero, long_decimal in numeros_decimales:
            if valor is None:
                if obligatorio:
                    raise Exception(
                        f"{nombre} es obligatorio."
                    )
                else:
                    continue

            if not 0 <= valor < 10**long_entero:
                raise Exception(
                    f"{nombre} no es valido. Debe contener, como máximo, {long_entero} digitos para la parte entera "
                    f"y {long_decimal} decimales."
                )

    def _validar_dia_inicio_situaciones_revista(self):
        dia_inicio_situacion_revista_1 = self.datos.dia_inicio_situacion_revista_1
        dia_inicio_situacion_revista_2 = self.datos.dia_inicio_situacion_revista_2
        dia_inicio_situacion_revista_3 = self.datos.dia_inicio_situacion_revista_3

        if dia_inicio_situacion_revista_1 and not 0 <= dia_inicio_situacion_revista_1 <= 31:
            raise Exception(
                "El dia de inicio de situacion de revista 1 no es valida. Debe contener, como máximo, 2 digitos."
            )

        if dia_inicio_situacion_revista_2 and not 0 <= dia_inicio_situacion_revista_2 <= 31:
            raise Exception(
                "El dia de inicio de situacion de revista 2 no es valida. Debe contener, como máximo, 2 digitos."
            )

        if dia_inicio_situacion_revista_3 and not 0 <= dia_inicio_situacion_revista_3 <= 31:
            raise Exception(
                "El dia de inicio de situacion de revista 3 no es valida. Debe contener, como máximo, 2 digitos."
            )

    def _validar_cantidad_hijos(self):
        cantidad_hijos = self.datos.cantidad_hijos

        if cantidad_hijos and not 0 <= cantidad_hijos <= 99:
            raise Exception(
                "La cantidad de hijos no es valida. Debe contener, como máximo, 2 digitos."
            )

    def _validar_tiempo_trabajado(self):
        cantidad_dias_trabajados = self.datos.cantidad_dias_trabajados
        cantidad_horas_trabajadas = self.datos.cantidad_horas_trabajadas

        if cantidad_dias_trabajados:
            if cantidad_dias_trabajados < 0:
                raise Exception(
                    "Cantidad de dias trabajados no puede ser un valor negativo."
                )

            if cantidad_dias_trabajados > 0 and cantidad_horas_trabajadas and cantidad_horas_trabajadas > 0:
                raise Exception(
                    "Cantidad de dias trabajados y cantidad de horas trabajadas son mutuamente excluyentes."
                )

            if not cantidad_dias_trabajados <= 99:
                raise Exception(
                    "La cantidad de dias trabajados no es valida. Debe contener, como máximo, 2 digitos."
                )

        if cantidad_horas_trabajadas:
            if cantidad_horas_trabajadas < 0:
                raise Exception(
                    "Cantidad de horas trabajados no puede ser un valor negativo."
                )

            if cantidad_horas_trabajadas > 0 and cantidad_dias_trabajados and cantidad_dias_trabajados > 0:
                raise Exception(
                    "Cantidad de dias trabajados y cantidad de horas trabajadas son mutuamente excluyentes."
                )

            if not cantidad_horas_trabajadas <= 999:
                raise Exception(
                    "La cantidad de horas trabajadas no es valida. Debe contener, como máximo, 3 digitos."
                )

    def _validar_cantidad_adherentes_obra_social(self):
        cantidad_adherentes_obra_social = self.datos.cantidad_adherentes_obra_social

        if cantidad_adherentes_obra_social and not 0 <= cantidad_adherentes_obra_social <= 99:
            raise Exception(
                "La cantidad de adherentes a la obra social no es valida. Debe contener, como máximo, 2 digitos."
            )
