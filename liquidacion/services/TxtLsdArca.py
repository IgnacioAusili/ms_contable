from liquidacion.lsd.registro01 import GeneradorRegistro01, DatosRegistro01
from liquidacion.lsd.registro02 import GeneradorRegistro02, DatosRegistro02
from liquidacion.lsd.registro03 import GeneradorRegistro03, DatosRegistro03
from liquidacion.lsd.registro04 import GeneradorRegistro04, DatosRegistro04
from liquidacion.lsd.mappers import Registro01Mapper, Registro02Mapper, Registro03Mapper, Registro04Mapper
from liquidacion.models import Liquidacion


class LsdTxtArcaService:
    """
    Archivo de texto con extensión “.txt” y formato de codificación “ANSI”
    Cada tipo de registro debe venir informado en una línea, uno debajo del otro
    Tipos de registro permitidos:
    - Registros tipo 01: Obligatorio. Para informar datos referenciales de la liquidación en el archivo a ingresar
    - Registros tipo 02: Cuando identificacion de envio='SJ'. Con datos generales de la liquidación de sueldo
      de cada trabajador
    - Registros tipo 03: Cuando identificacion de envio='SJ'. Es el detalle de los conceptos de sueldo liquidados a
      cada trabajador
    - Registros tipo 04: Obligatorio. Atributos de la relación laboral de cada trabajador para la determinación de
      las deudas con el SUSS
    - Registros tipo 05: Opcional. Información detallada de los trabajadores eventuales para la emisión del
      Libro Especial, Dec. 342/1992
    - Registros tipo 06 - Opcional. Campo de Observaciones: Es un campo opcional a completar con información que
      resulte útil para el empleador.
    """
    def __init__(self, liquidacion: Liquidacion):
        self.liquidacion = liquidacion

    def generar(self):
        pass
