import math
from dataclasses import dataclass
from decimal import Decimal
from xml.sax.saxutils import escape


@dataclass
class ComposicionCostoLaboral:
    neto: Decimal
    sindical: Decimal
    seguridad_social: Decimal
    obra_social: Decimal
    inssjp: Decimal
    art_scvo: Decimal
    entidades_empresariales: Decimal
    otros: Decimal


class GraficoCostoLaboralService:

    COLORES = [
        "#4E79A7",  # Azul
        "#F28E2B",  # Naranja
        "#E15759",  # Rojo
        "#76B7B2",  # Verde azulado
        "#59A14F",  # Verde
        "#EDC948",  # Amarillo
        "#B07AA1",  # Violeta
        "#FF9DA7",  # Rosa
    ]

    def __init__(self, composicion: ComposicionCostoLaboral):
        self.composicion = composicion

    def _obtener_valores(self):
        return {
            "Neto": self.composicion.neto,
            "Sindical": self.composicion.sindical,
            "Seguridad social": self.composicion.seguridad_social,
            "Obra social": self.composicion.obra_social,
            "INSSJP": self.composicion.inssjp,
            "ART + SCVO": self.composicion.art_scvo,
            "Entidades empresariales": self.composicion.entidades_empresariales,
            "Otros": self.composicion.otros,
        }

    def generar_svg(self):
        valores = self._obtener_valores()
        total = sum(valores.values(), Decimal("0"))

        if total <= 0:
            return ""

        width = 360
        height = 220

        cx = 90
        cy = 110
        radius = 75

        partes = []

        angulo_actual = -math.pi / 2

        for indice, (nombre, valor) in enumerate(valores.items()):
            if valor <= 0:
                continue

            proporcion = float(valor / total)
            angulo = proporcion * 2 * math.pi

            angulo_fin = angulo_actual + angulo

            partes.append(
                self._generar_sector(
                    cx=cx,
                    cy=cy,
                    radio=radius,
                    angulo_inicio=angulo_actual,
                    angulo_fin=angulo_fin,
                    color=self.COLORES[indice % len(self.COLORES)],
                )
            )

            angulo_actual = angulo_fin

        leyenda = self._generar_leyenda(
            valores,
            total,
            x=185,
            y=35,
        )

        return f"""
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}"
        role="img"
        aria-label="Composición del costo total empleador"
    >
        <g>
            {"".join(partes)}
        </g>

        {leyenda}
    </svg>
    """.strip()

    @staticmethod
    def _generar_sector(
        cx,
        cy,
        radio,
        angulo_inicio,
        angulo_fin,
        color,
    ):
        x1 = cx + radio * math.cos(angulo_inicio)
        y1 = cy + radio * math.sin(angulo_inicio)

        x2 = cx + radio * math.cos(angulo_fin)
        y2 = cy + radio * math.sin(angulo_fin)

        arco_largo = 1 if angulo_fin - angulo_inicio > math.pi else 0

        # Caso especial: círculo completo.
        if arco_largo == 1 and abs(
            (angulo_fin - angulo_inicio) - 2 * math.pi
        ) < 0.000001:
            return f"""
<circle
    cx="{cx}"
    cy="{cy}"
    r="{radio}"
    fill="{color}"
    stroke="#FFFFFF"
    stroke-width="1"
/>
"""

        return f"""
<path
    d="
        M {cx} {cy}
        L {x1:.4f} {y1:.4f}
        A {radio} {radio}
        0 {arco_largo} 1
        {x2:.4f} {y2:.4f}
        Z
    "
    fill="{color}"
    stroke="#FFFFFF"
    stroke-width="1"
/>
"""

    def _generar_leyenda(self, valores, total, x, y):
        elementos = []

        indice_color = 0

        for nombre, valor in valores.items():
            if valor <= 0:
                continue

            porcentaje = valor / total * 100
            color = self.COLORES[indice_color % len(self.COLORES)]

            elementos.append(
                f"""
    <rect
        x="{x}"
        y="{y - 9}"
        width="10"
        height="10"
        fill="{color}"
    />

    <text
        x="{x + 16}"
        y="{y}"
        font-family="Arial, sans-serif"
        font-size="11"
        fill="#222222"
    >
        {escape(nombre)} ({porcentaje:.1f}%)
    </text>
    """
            )

            y += 25
            indice_color += 1

        return "".join(elementos)
