from decimal import Decimal
from django.db import transaction

from base_imponible.models import BaseImponible, ResultadoBaseImponible
from liquidacion.models import LiquidacionEmpleado


class LiquidacionEmpleadoService:

    def __init__(self, liquidacion_empleado: LiquidacionEmpleado):
        self.liquidacion_empleado = liquidacion_empleado
        self.importes = {}

        self.detalles = {}
        self.resultados_bases = {}
        self.nodos_por_identificador = {}

    @transaction.atomic
    def crear(self):
        """
        Inicializa una liquidación de empleado recién creada.

        Crea los resultados de todas las bases imponibles que deben existir
        para la liquidación del empleado. Los valores son inicializados en
        cero y serán calculados posteriormente por liquidar().
        """
        self.crear_resultados_bases_imponibles()

    def crear_resultados_bases_imponibles(self):
        """
        Crea los resultados de las bases imponibles correspondientes a la
        liquidación del empleado.

        Este método debe ejecutarse una vez, inmediatamente después de crear
        el LiquidacionEmpleado.
        """
        bases = BaseImponible.objects.all()

        ResultadoBaseImponible.objects.bulk_create([
            ResultadoBaseImponible(
                liquidacion_empleado=self.liquidacion_empleado,
                base_imponible=base,
                importe=Decimal("0"),
            )
            for base in bases
        ])
