class ErrorCalculoLiquidacion(Exception):
    pass


class ReferenciaInexistente(ErrorCalculoLiquidacion):
    pass


class VersionConceptoNoLiquidada(ErrorCalculoLiquidacion):
    pass


class ReferenciaCiclica(ErrorCalculoLiquidacion):
    pass


class ExpresionBaseInvalida(ErrorCalculoLiquidacion):
    pass


class DetalleFueraDeLiquidacion(Exception):
    pass
