from decimal import Decimal
from num2words import num2words
from concepto.models import VersionConcepto
from grupo_concepto.models import GrupoConcepto
from liquidacion.models import LiquidacionEmpleado
from liquidacion.services.GraficoCostoLaboralService import GraficoCostoLaboralService


class ReciboSueldoService:

    def __init__(self, liquidacion_empleado):
        self.liquidacion_empleado = (
            LiquidacionEmpleado.objects
            .select_related(
                "liquidacion",
                "empleado",
                "empleado__empresa",
            )
            .prefetch_related(
                "detalles__concepto",
                "detalles__concepto__grupo",
            )
            .get(pk=liquidacion_empleado.pk)
        )

    def obtener_datos(self, tipo):
        le = self.liquidacion_empleado
        liquidacion = le.liquidacion
        empleado = le.empleado
        empresa = empleado.empresa

        detalles = list(le.detalles.all())

        remunerativos = [
            self._detalle_a_dict(detalle)
            for detalle in detalles
            if detalle.concepto.tipo == VersionConcepto.Tipo.REMUNERATIVO
        ]

        no_remunerativos = [
            self._detalle_a_dict(detalle)
            for detalle in detalles
            if detalle.concepto.tipo == VersionConcepto.Tipo.NO_REMUNERATIVO
        ]

        descuentos = [
            self._detalle_a_dict(detalle)
            for detalle in detalles
            if detalle.concepto.tipo == VersionConcepto.Tipo.DESCUENTO
        ]

        contribuciones = [
            self._detalle_a_dict(detalle)
            for detalle in detalles
            if detalle.concepto.tipo == VersionConcepto.Tipo.CONTRIBUCION
        ]

        detalle = self.obtener_detalle_grupos(detalles)

        grafico_torta_svg = GraficoCostoLaboralService(
            detalle=detalle,
            remuneracion_neta=le.neto,
        ).generar_svg()

        return {
            "tipo": tipo,
            "empresa": {
                "nombre": empresa.nombre,
                "domicilio": liquidacion.domicilio_empresa,
                "cuit": empresa.cuit,
            },

            "mes": liquidacion.periodo.month,
            "anio": liquidacion.periodo.year,

            "empleado": {
                "apellido_nombre": (
                    f"{empleado.apellidos}, {empleado.nombres}"
                ),
                "legajo": empleado.legajo,
                "sueldo_bruto": self._decimal_a_string(le.bruto),
                "antiguedad": f"{self.calcular_antiguedad(empleado.fecha_ingreso, liquidacion.fecha_pago,)} AÑOS",
                "fecha_ingreso": empleado.fecha_ingreso.strftime("%d/%m/%Y"),
                "categoria": le.categoria,
                "cuil": empleado.cuil_display,
                "banco": le.banco_de_cobro,
                "periodo_pago": f"{liquidacion.fecha_pago.strftime('%d/%m/%Y')}",
            },

            "contribuciones": contribuciones,
            "remunerativos": remunerativos,
            "no_remunerativos": no_remunerativos,
            "descuentos": descuentos,

            "costo_total_empleador": self._decimal_a_string(
                le.costo_laboral
            ),
            "subtotal_contribuciones": self._decimal_a_string(
                le.contribuciones
            ),
            "sueldo_bruto": self._decimal_a_string(le.bruto),
            "total_remunerativo": self._decimal_a_string(
                le.remunerativo
            ),
            "total_no_remunerativo": self._decimal_a_string(
                le.no_remunerativo
            ),
            "total_descuentos": self._decimal_a_string(
                le.descuentos
            ),
            "sueldo_neto": self._decimal_a_string(int(le.neto)),

            "neto_en_letras": self.neto_en_letras(le.neto),

            "observaciones": le.observaciones if le.observaciones else "-",

            "detalle": detalle,

            "grafico_torta_svg": grafico_torta_svg,
        }

    def _detalle_a_dict(self, detalle):
        concepto = detalle.concepto

        return {
            "concepto": concepto.denominacion,
            "unidad": self._formatear_unidad(
                concepto.unidad,
                detalle.unidades,
            ),
            "base": self._decimal_a_string(detalle.base),
            "monto": self._decimal_a_string(detalle.importe),
        }

    def obtener_detalle_grupos(self, detalles):
        resultado = {}

        for grupo in GrupoConcepto.objects.all().order_by("id"):
            detalles_grupo = [
                detalle
                for detalle in detalles
                if detalle.concepto.grupo_id == grupo.id
            ]

            total = sum(
                (detalle.importe for detalle in detalles_grupo),
                Decimal("0"),
            )

            empleador = sum(
                (
                    detalle.importe
                    for detalle in detalles_grupo
                    if detalle.concepto.categoria
                       == VersionConcepto.Categoria.EMPLEADOR
                ),
                Decimal("0"),
            )

            trabajador = sum(
                (
                    detalle.importe
                    for detalle in detalles_grupo
                    if detalle.concepto.categoria
                       == VersionConcepto.Categoria.TRABAJADOR
                ),
                Decimal("0"),
            )

            resultado[grupo.codigo] = {
                "denominacion": grupo.denominacion,
                "total": self._decimal_a_string(total),
                "empleador": self._decimal_a_string(empleador),
                "trabajador": self._decimal_a_string(trabajador),
            }

        return resultado

    @staticmethod
    def calcular_antiguedad(fecha_ingreso, fecha_referencia):
        if fecha_ingreso > fecha_referencia:
            raise ValueError(
                "La fecha de ingreso no puede ser posterior "
                "a la fecha de referencia."
            )

        anios = fecha_referencia.year - fecha_ingreso.year

        if (
            fecha_referencia.month,
            fecha_referencia.day,
        ) < (
            fecha_ingreso.month,
            fecha_ingreso.day,
        ):
            anios -= 1

        return anios

    @staticmethod
    def _formatear_unidad(unidad, unidades):
        return f"{unidades:.2f} {VersionConcepto.Unidad(unidad).sufijo}"

    @staticmethod
    def _decimal_a_string(valor):
        if valor is None:
            return None

        return str(valor)

    @staticmethod
    def neto_en_letras(valor):
        return num2words(
            int(valor),
            lang="es",
        )
