from decimal import Decimal
from django.db import transaction
from django.db.models import Prefetch
import ast, operator
from simpleeval import SimpleEval
from base_imponible.models import ResultadoBaseImponible
from liquidacion.models import LiquidacionEmpleado, DetalleLiquidacion
from ..validators.v_expresiones import preparar_formula
from ..exceptions import ReferenciaInexistente, ReferenciaCiclica, VersionConceptoNoLiquidada
from concepto.models import VersionConcepto


class LiquidacionEmpleadoService:
    OPERADORES = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.Pow: operator.pow,
    }

    def __init__(self, liquidacion_empleado: LiquidacionEmpleado):
        self.liquidacion_empleado = liquidacion_empleado
        self.importes = {}

        self.detalles = {}
        self.resultados_bases = {}
        self.nodos_por_identificador = {}

    @transaction.atomic
    def liquidar(self):
        self.calcular_importes_para_detalles()
        self.calcular_subtotales_empleado()

    def cargar_datos_calculo(self):
        """
        Carga en memoria los detalles y resultados de bases imponibles de la
        liquidación y construye el índice de nodos por identificador.

        Los identificadores de los detalles provienen del concepto utilizado
        por cada detalle, mientras que los identificadores de los resultados
        de bases imponibles provienen de su BaseImponible.

        El índice permite resolver referencias de fórmulas sin realizar
        consultas adicionales a la base de datos durante el cálculo.
        """
        detalles = (
            DetalleLiquidacion.objects
            .filter(liquidacion_empleado=self.liquidacion_empleado,)
            .select_related("concepto")
        )

        empresa_id = self.liquidacion_empleado.liquidacion.empresa_id

        versiones = VersionConcepto.todos.filter(concepto__empresa_id=empresa_id)

        resultados_bases = (
            ResultadoBaseImponible.objects
            .filter(liquidacion_empleado=self.liquidacion_empleado,)
            .select_related("base_imponible")
            .prefetch_related(
                Prefetch(
                    "base_imponible__versiones_concepto",
                    queryset=versiones,
                )
            )
        )

        self.detalles = {
            ("detalle", detalle.id): detalle
            for detalle in detalles
        }

        self.resultados_bases = {
            ("base", resultado.id): resultado
            for resultado in resultados_bases
        }

        self.nodos_por_identificador = {}

        for nodo, detalle in self.detalles.items():
            self._registrar_nodo(detalle.concepto.identificador_version, nodo,)

        for nodo, resultado_base in self.resultados_bases.items():
            self._registrar_nodo(resultado_base.base_imponible.identificador, nodo,)

    def _registrar_nodo(self, identificador, nodo):
        """
        Registra un nodo en el índice de identificadores.

        Un identificador debe ser único dentro del contexto de una
        liquidación de empleado, independientemente de si pertenece a un
        detalle o a una base imponible.
        """
        if identificador in self.nodos_por_identificador:
            raise ValueError(
                f"El identificador '{identificador}' "
                "está definido para más de un nodo."
            )

        self.nodos_por_identificador[identificador] = nodo

    def calcular_subtotales_empleado(self):
        """
        Calcula y persiste los subtotales de la liquidación del empleado
        a partir de los importes de sus detalles.

        Los subtotales se agrupan según el tipo económico del concepto:
        remunerativo, no remunerativo, descuento y contribución.
        """
        detalles = self.detalles.values()

        subtotales = {
            VersionConcepto.Tipo.REMUNERATIVO: Decimal("0"),
            VersionConcepto.Tipo.NO_REMUNERATIVO: Decimal("0"),
            VersionConcepto.Tipo.DESCUENTO: Decimal("0"),
            VersionConcepto.Tipo.CONTRIBUCION: Decimal("0"),
        }

        for detalle in detalles:
            tipo = detalle.concepto.tipo

            if tipo not in subtotales:
                raise ValueError(
                    f"Tipo de concepto no soportado: {tipo}"
                )

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
        contribuciones = subtotales[
            VersionConcepto.Tipo.CONTRIBUCION
        ]

        remuneracion_bruta = self.obtener_valor_base_imponible("remuneracion_total")

        remuneracion_neta = (
            remuneracion_bruta
            - descuentos
        )

        costo = (
            remuneracion_bruta
            + contribuciones
        )

        liquidacion_empleado = self.liquidacion_empleado

        liquidacion_empleado.remunerativo = remunerativo
        liquidacion_empleado.no_remunerativo = no_remunerativo
        liquidacion_empleado.descuentos = descuentos
        liquidacion_empleado.contribuciones = contribuciones
        liquidacion_empleado.bruto = remuneracion_bruta
        liquidacion_empleado.neto = remuneracion_neta
        liquidacion_empleado.costo_laboral = costo

        liquidacion_empleado.save(
            update_fields=[
                "remunerativo",
                "no_remunerativo",
                "descuentos",
                "contribuciones",
                "bruto",
                "neto",
                "costo_laboral",
            ]
        )

    def calcular_importes_para_detalles(self):
        """
        Calcula todos los detalles y resultados de bases imponibles
        respetando el orden determinado por sus dependencias.
        """
        try:
            self.cargar_datos_calculo()

            grafo_referencias = obtener_grafo_referencias(
                self.detalles,
                self.resultados_bases,
                self.nodos_por_identificador,
            )

            orden_calculos = obtener_orden_calculo(
                grafo_referencias
            )

            for nodo in orden_calculos:
                if nodo[0] == "detalle":
                    self.evaluar_y_asignar_importe(
                        self.detalles[nodo]
                    )
                elif nodo[0] == "base":
                    self.calcular_y_asignar_base_imponible(
                        self.resultados_bases[nodo]
                    )
                else:
                    raise ValueError(
                        f"Tipo de nodo no soportado: {nodo[0]}"
                    )

            DetalleLiquidacion.objects.bulk_update(
                self.detalles.values(),
                ["base", "importe"],
            )

            ResultadoBaseImponible.objects.bulk_update(
                self.resultados_bases.values(),
                ["importe"],
            )
        except Exception as e:
            raise e  # pending, raise custom exception(s)

    def evaluar_y_asignar_importe(self, detalle):
        """
        Evalúa la fórmula base de un detalle y calcula su importe según
        la unidad del concepto.
        """
        base = self.evaluar_formula(detalle.formula_base)
        detalle.base = base

        unidad = VersionConcepto.Unidad(detalle.concepto.unidad)
        importe = unidad.calcular_importe(
            detalle.unidades,
            base,
        )

        detalle.importe = importe

        self.importes[("detalle", detalle.id)] = importe

        return importe

    def calcular_y_asignar_base_imponible(self, resultado_base):
        """
        Calcula y asigna el importe de un resultado de base imponible.

        Algunas bases tienen un cálculo específico y no se obtienen a partir
        de las versiones de conceptos asociadas a la base.
        """
        identificador = resultado_base.base_imponible.identificador

        if identificador == "detracciones":
            importe = resultado_base.importe

        elif identificador == "remuneracion_total":
            importe = self.calcular_remuneracion_total()

        elif identificador == "remuneracion_10":
            importe = self.calcular_remuneracion_10()

        else:
            importe = self.calcular_base_imponible_por_conceptos(
                resultado_base
            )

        resultado_base.importe = importe

        self.importes[("base", resultado_base.id)] = importe

        return importe

    def calcular_remuneracion_total(self):
        """
        Calcula la remuneración total como el bruto de la liquidación.

        El bruto está compuesto por los importes remunerativos y
        no remunerativos de los detalles de la liquidación.
        """
        importe = Decimal("0")

        for nodo, detalle in self.detalles.items():
            if detalle.concepto.tipo in (
                    VersionConcepto.Tipo.REMUNERATIVO,
                    VersionConcepto.Tipo.NO_REMUNERATIVO,
            ):
                try:
                    importe += self.importes[nodo]
                except KeyError:
                    raise RuntimeError(
                        f"El detalle '{detalle.concepto.identificador_version}' "
                        "todavía no fue calculado."
                    )

        return importe

    def calcular_remuneracion_10(self):
        """
        Calcula remuneracion_10 como remuneracion_2 menos detracciones.
        """
        nodo_remuneracion_2 = self.nodos_por_identificador.get(
            "remuneracion_2"
        )
        nodo_detracciones = self.nodos_por_identificador.get(
            "detracciones"
        )

        if nodo_remuneracion_2 is None:
            raise ReferenciaInexistente("remuneracion_2")

        if nodo_detracciones is None:
            raise ReferenciaInexistente("detracciones")

        try:
            remuneracion_2 = self.importes[nodo_remuneracion_2]
            detracciones = self.importes[nodo_detracciones]
        except KeyError as e:
            raise RuntimeError(
                f"El nodo '{e.args[0]}' todavía no fue calculado."
            )

        return remuneracion_2 - detracciones

    def calcular_base_imponible_por_conceptos(self, resultado_base):
        versiones = (
            resultado_base.base_imponible
            .versiones_concepto
            .all()
        )

        importe = Decimal("0")

        for version in versiones:
            nodo = self.nodos_por_identificador.get(version.identificador_version)

            if nodo:
                try:
                    importe += self.importes[nodo]
                except KeyError:
                    raise RuntimeError(
                        f"El nodo '{version.identificador_version}' "
                        "todavía no fue calculado."
                    )

        return importe

    def evaluar_formula(self, formula):
        """
        Evalúa una fórmula utilizando los valores calculados de sus
        referencias a detalles y bases imponibles.
        """
        try:
            formula_normalizada = normalizar_formula(formula)
            referencias = self.resolver_referencias(
                formula_normalizada
            )
            expresion_evaluable, valores_numericos = preparar_formula(
                formula_normalizada
            )

            evaluador = SimpleEval(
                operators=self.OPERADORES,
                names={
                    **referencias,
                    **valores_numericos,
                },
            )

            return evaluador.eval(
                expr=expresion_evaluable,
            )
        except Exception as e:
            raise e  # pending, raise custom exception(s)

    def resolver_referencias(self, expresion):
        """
        Resuelve los identificadores utilizados en una fórmula utilizando
        los nodos cargados previamente en memoria.

        El valor de cada referencia debe haber sido calculado antes de
        evaluar la fórmula, condición garantizada por el orden topológico
        obtenido a partir del grafo de dependencias.
        """
        identificadores = obtener_identificadores(expresion)

        referencias = {}

        for identificador in identificadores:
            try:
                nodo = self.nodos_por_identificador[identificador]
            except KeyError:
                raise ReferenciaInexistente(identificador)

            try:
                referencias[identificador] = self.importes[nodo]
            except KeyError:
                raise RuntimeError(
                    f"El nodo '{identificador}' "
                    "todavía no fue calculado."
                )

        return referencias

    def obtener_valor_base_imponible(self, identificador):
        nodo = self.nodos_por_identificador.get(identificador)

        if nodo is None:
            raise ReferenciaInexistente(identificador)

        try:
            return self.importes[nodo]
        except KeyError:
            raise RuntimeError(
                f"La base imponible '{identificador}' "
                "todavía no fue calculada."
            )


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
    Valida que el grafo de dependencias de una liquidación de empleado no contenga ciclos y obtiene un orden
    válido para realizar los cálculos.

    El grafo puede contener dos tipos de nodos:
        - DetalleLiquidacion.
        - ResultadoBaseImponible.

    Cada nodo representa un valor que debe ser calculado y cada arista dirigida representa una dependencia desde
    el nodo origen hacia el nodo requerido para calcularlo.

    La dirección de las aristas es: nodo -> dependencia

    Por ejemplo: obra_social -> remuneracion_1 -> sueldo_basico

    El grafo se representa como un diccionario de adyacencia:
        {
            nodo_origen: [nodo_dependencia, ...],
            ...
        }

    El orden devuelto garantiza que una dependencia aparezca antes que cualquier nodo que necesite su resultado.
    Esto permite calcular secuencialmente todos los nodos sin intentar utilizar un valor que aún no haya sido obtenido.

    La validación se realiza sobre todos los nodos del grafo, incluyendo componentes que no estén conectados entre sí.
    De esta forma se garantiza que ninguna dependencia circular quede sin detectar.

    Raises:
        ReferenciaCiclica: si se encuentra un ciclo de dependencias.
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


def obtener_grafo_referencias(
    detalles,
    resultados_bases,
    nodos_por_identificador,
):
    """
    Construye el grafo de dependencias de una liquidación a partir de los
    datos previamente cargados en memoria.

    El grafo contiene como nodos los detalles de liquidación y los
    resultados de bases imponibles. Cada nodo apunta a los nodos de los
    que depende.

    Las dependencias de los detalles surgen de los identificadores
    utilizados en sus fórmulas.

    Las dependencias de los resultados de bases imponibles surgen de los
    conceptos que componen cada base imponible. Una base puede estar
    asociada a distintas versiones de un mismo concepto; en ese caso,
    se utiliza como dependencia la versión que fue utilizada en la
    liquidación.

    La dirección de las aristas es:

        nodo -> dependencia

    Args:
        detalles: Diccionario de nodos de tipo "detalle", indexados por
            ("detalle", id).
        resultados_bases: Diccionario de nodos de tipo "base", indexados
            por ("base", id).
        nodos_por_identificador: Índice que relaciona cada identificador
            con su nodo correspondiente.

    Raises:
        ReferenciaInexistente: si una fórmula referencia un identificador
            que no existe.
        VersionConceptoNoLiquidada: si una base imponible referencia un
            concepto para el cual ninguna de sus versiones fue utilizada
            en la liquidación.
    """

    grafo = {
        nodo: []
        for nodo in (
            *detalles.keys(),
            *resultados_bases.keys(),
        )
    }

    for nodo, detalle in detalles.items():
        formula_normalizada = normalizar_formula(detalle.formula_base)

        identificadores = obtener_identificadores(formula_normalizada)

        for identificador in identificadores:
            try:
                nodo_referenciado = nodos_por_identificador[identificador]
            except KeyError:
                raise ReferenciaInexistente(identificador)

            grafo[nodo].append(nodo_referenciado)

    for nodo, resultado_base in resultados_bases.items():
        identificador_base = resultado_base.base_imponible.identificador

        if identificador_base == "detracciones":
            continue

        if identificador_base == "remuneracion_10":
            for identificador in ("remuneracion_2", "detracciones",):
                try:
                    nodo_referenciado = nodos_por_identificador[identificador]
                except KeyError:
                    raise ReferenciaInexistente(identificador)

                grafo[nodo].append(nodo_referenciado)

            continue

        if identificador_base == "remuneracion_total":
            for nodo_detalle, detalle in detalles.items():
                if detalle.concepto.tipo in (
                        VersionConcepto.Tipo.REMUNERATIVO,
                        VersionConcepto.Tipo.NO_REMUNERATIVO,
                ):
                    grafo[nodo].append(nodo_detalle)

            continue

        # todas las versiones de concepto que el usuario marco para que computen como parte del resultado_base
        versiones = resultado_base.base_imponible.versiones_concepto.all()

        # Una base sin conceptos asociados no tiene dependencias.
        if not versiones:
            continue

        versiones_por_concepto = {}

        for version in versiones:
            versiones_por_concepto.setdefault(version.concepto_id, []).append(version)

        for versiones_concepto in versiones_por_concepto.values():
            for version in versiones_concepto:
                nodo_referenciado = nodos_por_identificador.get(version.identificador_version)

                if nodo_referenciado is not None:
                    # agregar los detalles de liquidacion y bases que seran dependencias para poder calcular
                    # la base en cuestion
                    grafo[nodo].append(nodo_referenciado)

    return grafo


def agregar_nodo_por_identificador(
    nodos_por_identificador,
    identificador,
    nodo,
):
    if identificador in nodos_por_identificador:
        raise ValueError(
            f"El identificador '{identificador}' "
            "está definido para más de un nodo."
        )

    nodos_por_identificador[identificador] = nodo
