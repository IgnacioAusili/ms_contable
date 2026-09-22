"""
Filtros para la plantilla del recibo de sueldo.

Ubicación: <app>/templatetags/recibo_tags.py   (junto con un __init__.py vacío)
Uso en la plantilla: {% load recibo_tags %}

Los importes se formatean siempre como 2,346,810.31 (coma de miles, punto decimal),
sin depender del LANGUAGE_CODE ni de USE_THOUSAND_SEPARATOR.
"""
from decimal import Decimal, InvalidOperation

from django import template
from django.utils.html import format_html

register = template.Library()


def _formatear(value):
    """Devuelve '' si no hay valor; si no es numérico, lo devuelve tal cual."""
    if value is None or value == "":
        return ""
    try:
        numero = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return str(value)
    return f"{numero:,.2f}"


@register.filter
def monto(value):
    """2346810.3 -> '2,346,810.30'  (None o '' -> '')."""
    return _formatear(value)


@register.filter
def moneda(value):
    """
    Igual que `monto`, pero con el signo $ alineado a la izquierda de la celda:
    2346810.3 -> '<i>$</i>2,346,810.30'  (None o '' -> '', sin signo).
    Un valor 0 sí se muestra ('$0.00'); para dejar la celda vacía enviar None.
    """
    texto = _formatear(value)
    if texto == "":
        return ""
    return format_html("<i>$</i>{}", texto)
