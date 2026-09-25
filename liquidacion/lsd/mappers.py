from liquidacion.lsd.registro01 import DatosRegistro01
from liquidacion.lsd.registro02 import DatosRegistro02
from liquidacion.lsd.registro03 import DatosRegistro03
from liquidacion.lsd.registro04 import DatosRegistro04

"""
Consideraciones generales:
- Los campos definidos como alfanuméricos deben informarse con espacios a la derecha hasta completar la longitud indicada
- Los campos definidos como numéricos deben informarse con ceros (0) a la izquierda hasta completar la longitud indicada
- Los campos definidos como decimales deben informarse sin separador decimal. Se consideran las dos últimas posiciones 
  del valor informado como los centavos del número.
"""


class Registro01Mapper:
    def obtener_datos(self, liquidacion) -> DatosRegistro01:
        pass

        # return DatosRegistro01(
        #     cuit=...
        #     ...
        # )


class Registro02Mapper:
    def obtener_datos(self, liquidacion) -> DatosRegistro01:
        pass

        # return DatosRegistro01(
        #     cuit=...
        #     ...
        # )


class Registro03Mapper:
    def obtener_datos(self, liquidacion) -> DatosRegistro01:
        pass

        # return DatosRegistro01(
        #     cuit=...
        #     ...
        # )


class Registro04Mapper:
    def obtener_datos(self, liquidacion) -> DatosRegistro01:
        pass

        # return DatosRegistro01(
        #     cuit=...
        #     ...
        # )

