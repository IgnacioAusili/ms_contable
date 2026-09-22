from decimal import Decimal
from django.db import transaction
import ast, operator
from simpleeval import SimpleEval
from liquidacion.models import LiquidacionEmpleado, DetalleLiquidacion
from ..validators.v_expresiones import preparar_formula
from ..exceptions import ReferenciaInexistente, ReferenciaCiclica
from concepto.models import VersionConcepto


class LiquidacionEmpleadoService:
    OPERADORES={
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.Pow: operator.pow,
    }

    def __init__(self, liquidacion_empleado: LiquidacionEmpleado):
        self.liquidacion_empleado = liquidacion_empleado
        self.importes = {}  # { detalle_id: importe_calculado, }

    @transaction.atomic
    def liquidar(self):
        self.calcular_importes_para_detalles()
        self.calcular_subtotales_empleado()

    def calcular_subtotales_empleado(self):
        detalles = (
            DetalleLiquidacion.objects
            .filter(
                liquidacion_empleado=self.liquidacion_empleado,
            )
            .select_related("concepto")
        )

        subtotales = {
            VersionConcepto.Tipo.REMUNERATIVO: Decimal("0"),
            VersionConcepto.Tipo.NO_REMUNERATIVO: Decimal("0"),
            VersionConcepto.Tipo.DESCUENTO: Decimal("0"),
            VersionConcepto.Tipo.CONTRIBUCION: Decimal("0"),
            # VersionConcepto.Tipo.REDONDEO: Decimal("0"),
        }

        for detalle in detalles:
            tipo = detalle.concepto.tipo

            if tipo not in subtotales:
                continue  # TODO - ver que se debe hacer con los tipo=redondeo
                # raise ValueError(
                #     f"Tipo de concepto no soportado: {tipo}"
                # )

            subtotales[tipo] += detalle.importe

        remunerativo = subtotales[
            VersionConcepto.Tipo.REMUNERATIVO
        ]

        no_remunerativo = subtotales[
            VersionConcepto.Tipo.NO_REMUNERATIVO
        ]

        descuentos = subtotales[
            VersionConcepto.Tipo.DESCUENTO
        ]

        # redondeo = subtotales[
        #     VersionConcepto.Tipo.REDONDEO
        # ]

        contribuciones = subtotales[
            VersionConcepto.Tipo.CONTRIBUCION
        ]

        remuneracion_bruta = (
            remunerativo
            + no_remunerativo
        )

        remuneracion_neta = (
            remuneracion_bruta
            - descuentos
            # + redondeo
        )

        costo = (
            remuneracion_bruta
            + contribuciones
        )

        liquidacion_empleado = self.liquidacion_empleado

        liquidacion_empleado.remunerativo = remunerativo
        liquidacion_empleado.no_remunerativo = no_remunerativo
        liquidacion_empleado.descuentos = descuentos
        # liquidacion_empleado.redondeo = redondeo
        liquidacion_empleado.contribuciones = contribuciones
        liquidacion_empleado.bruto = remuneracion_bruta
        liquidacion_empleado.neto = remuneracion_neta
        liquidacion_empleado.costo_laboral = costo

        liquidacion_empleado.save(
            update_fields=[
                "remunerativo",
                "no_remunerativo",
                "descuentos",
                # "redondeo",
                "contribuciones",
                "bruto",
                "neto",
                "costo_laboral",
            ]
        )

    def calcular_importes_para_detalles(self):
        try:
            grafo_referencias = obtener_grafo_referencias(self.liquidacion_empleado)
            orden_calculos = obtener_orden_calculo(grafo_referencias)

            detalles = {
                detalle.id: detalle
                for detalle in (
                    DetalleLiquidacion.objects
                    .filter(
                        id__in=orden_calculos,
                        liquidacion_empleado=self.liquidacion_empleado,
                    )
                    .select_related("concepto")
                )
            }

            for detalle_id in orden_calculos:
                self.evaluar_y_asignar_importe(detalles[detalle_id])

            DetalleLiquidacion.objects.bulk_update(
                detalles.values(),
                ["base", "importe"],
            )
        except Exception as e:
            raise e  # pending, raise custom exception(s)

    def evaluar_y_asignar_importe(self, detalle):
        base = self.evaluar_formula(detalle.formula_base)
        detalle.base = base

        unidad = VersionConcepto.Unidad(detalle.concepto.unidad)
        importe = unidad.calcular_importe(detalle.unidades, base)
        detalle.importe = importe

        self.importes[detalle.id] = importe

        return importe

    def evaluar_formula(self, formula):
        try:
            formula_normalizada = normalizar_formula(formula)
            referencias = self.resolver_referencias(formula_normalizada)
            expresion_evaluable, valores_numericos = preparar_formula(formula_normalizada)

            evaluador = SimpleEval(
                operators=self.OPERADORES,
                names={
                    **referencias,
                    **valores_numericos,
                },
            )

            return evaluador.eval(expr=expresion_evaluable)
        except Exception as e:
            raise e  # pending, raise custom exception(s)

    def resolver_referencias(self, expresion):
        identificadores = obtener_identificadores(expresion)

        if not identificadores:
            return {}

        detalles = (
            DetalleLiquidacion.objects
            .filter(
                liquidacion_empleado=self.liquidacion_empleado,
            )
            .select_related("concepto")
        )

        detalles_por_identificador = {
            detalle.concepto.identificador: detalle
            for detalle in detalles
        }

        referencias = {}

        for identificador in identificadores:
            try:
                detalle_referenciado = detalles_por_identificador[identificador]
            except KeyError:
                raise ReferenciaInexistente(identificador)

            try:
                importe = self.importes[detalle_referenciado.id]
            except KeyError:
                raise RuntimeError(f"El detalle '{identificador}' todavía no fue calculado.")

            referencias[identificador] = importe

        return referencias


def normalizar_formula(formula):
    return "".join(formula.split())


def obtener_identificadores(expresion):
    tree = ast.parse(expresion, mode="eval")

    return {
        nodo.id
        for nodo in ast.walk(tree)
        if isinstance(nodo, ast.Name)
    }


def obtener_orden_calculo(grafo):
    """
    Valida que el grafo completo de dependencias de una liquidación de empleado no contenga ciclos,
      y obtiene un orden de cálculo de los detalles de una liquidación.

    Estructura:
        Cada nodo representa un DetalleLiquidacion y cada arista dirigida representa una ReferenciaDetalle
          desde el detalle origen hacia el detalle referenciado.

        El grafo se representa como un diccionario de adyacencia:
            {
                id_detalle_origen: [id_detalle_referenciado, ...],
                ...
            }

    Alcance:
        La validación se realiza sobre todos los nodos del grafo, incluyendo componentes que no estén
          conectados entre sí. De esta forma se garantiza que ninguna dependencia circular quede sin detectar.

    Raises:
        ReferenciaCiclica: si se encuentra un ciclo de dependencias entre detalles de la liquidación.
    """
    visitados = set()
    en_camino = []
    orden = []

    def visitar(nodo):
        if nodo in en_camino:
            indice = en_camino.index(nodo)
            ciclo = en_camino[indice:] + [nodo]
            raise ReferenciaCiclica(ciclo)

        if nodo in visitados:
            return

        en_camino.append(nodo)

        for dependencia in grafo.get(nodo, []):
            visitar(dependencia)

        en_camino.pop()
        visitados.add(nodo)
        orden.append(nodo)

    for nodo in grafo:
        visitar(nodo)

    return orden


def obtener_grafo_referencias(liquidacion_empleado):
    detalles = (
        DetalleLiquidacion.objects
        .filter(liquidacion_empleado=liquidacion_empleado)
        .select_related("concepto")
    )

    detalles_por_identificador = {
        detalle.concepto.identificador: detalle
        for detalle in detalles
    }

    grafo = {
        detalle.id: []
        for detalle in detalles
    }

    for detalle in detalles:
        formula_normalizada = normalizar_formula(detalle.formula_base)
        identificadores = obtener_identificadores(formula_normalizada)

        for identificador in identificadores:
            try:
                detalle_referenciado = detalles_por_identificador[identificador]
            except KeyError:
                raise ReferenciaInexistente(identificador)

            grafo[detalle.id].append(detalle_referenciado.id)

    return grafo
