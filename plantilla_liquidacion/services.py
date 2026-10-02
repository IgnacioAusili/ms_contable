import re
from concepto.models import Concepto, VersionConcepto


class PlantillaLiquidacionService:
    IDENTIFICADOR_CONCEPTO_RE = re.compile(r"\b(?P<denominacion>[a-zA-Z_][a-zA-Z0-9_]*)_(?P<id>\d+)\b")

    def __init__(self, empresa):
        self.empresa = empresa

        versiones = (
            VersionConcepto.objects
            .filter(concepto__empresa=empresa)
            .ultima_version()
        )

        self._versiones = {version.concepto_id: version.identificador_version for version in versiones}

    def reemplazar_identificadores_formula(self, formula):
        def reemplazar(match):
            denominacion = match.group("denominacion")
            concepto_id = int(match.group("id"))

            if denominacion == "remuneracion":  # no es un concepto, es una base imponible. Los conceptos no pueden tener ese identificador
                return match.string

            if concepto_id not in self._versiones.keys():
                raise ValueError(
                    f"Concepto inexistente: {denominacion}_{concepto_id}"
                )

            return self._versiones.get(concepto_id)

        return self.IDENTIFICADOR_CONCEPTO_RE.sub(reemplazar, formula)
