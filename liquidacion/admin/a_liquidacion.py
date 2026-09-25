from django.contrib import admin

from .a_liquidacion_empleado import LiquidacionEmpleadoInline
from ..models.m_liquidacion import Liquidacion
from ..forms.f_liquidacion import LiquidacionForm


@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    form = LiquidacionForm
    inlines = [LiquidacionEmpleadoInline]
    actions = None

    list_display = (
        "__str__",
        "periodo",
        "fecha_pago",
        "tipo_envio",
        "tipo_liquidacion",
        "estado",
    )

    list_filter = ('empresa', 'estado',)
    list_select_related = ('empresa',)

    search_fields = ('periodo',)
    search_help_text = "Busqueda por periodo (fecha, año, mes, etc)"

    ordering = ('empresa', 'periodo',)

    change_form_template = "admin/liquidacion/change_form.html"
