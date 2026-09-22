import math
from decimal import Decimal
from xml.sax.saxutils import escape


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

    def __init__(self, detalle, remuneracion_bruta):
        self.detalle = detalle
        self.remuneracion_bruta = remuneracion_bruta

    def generar_svg(self):
        valores = self._obtener_valores()

        if not valores:
            return None

        total = sum(
            valores.values(),
            Decimal("0"),
        )

        if total <= 0:
            return None

        return self._generar_svg(valores, total)

    def _obtener_valores(self):
        valores = {}

        if self.remuneracion_bruta > 0:
            valores["Remuneración"] = self.remuneracion_bruta

        for codigo, datos in self.detalle.items():
            importe = datos.get("empleador")

            if importe is None:
                continue

            importe = Decimal(importe)

            if importe > 0:
                valores[datos["denominacion"]] = importe

        return valores

    def _generar_svg(self, valores, total):
        width = 360
        height = 220

        cx = 90
        cy = 110
        radius = 75

        partes = []

        angulo_actual = -math.pi / 2

        for indice, (nombre, valor) in enumerate(valores.items()):
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

        for indice, (nombre, valor) in enumerate(valores.items()):
            porcentaje = valor / total * 100
            color = self.COLORES[indice % len(self.COLORES)]

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

        return "".join(elementos)
