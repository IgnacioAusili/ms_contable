from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from core.utils import normalizar_identificador
from ..forms import LiquidacionEmpleadoInlineForm, LiquidacionEmpleadoInlineFormSet
from ..models import LiquidacionEmpleado
from ..models.m_liquidacion import Liquidacion
from ..forms.f_liquidacion import LiquidacionForm
from ..services.TxtLsdArca import LsdTxtArcaService


class LiquidacionEmpleadoInline(admin.TabularInline):
    model = LiquidacionEmpleado
    form = LiquidacionEmpleadoInlineForm
    formset = LiquidacionEmpleadoInlineFormSet

    extra = 0
    can_delete = True
    show_change_link = True

    fields = (
        "detalle_link",
        "empleado",
        "remunerativo_display",
        "no_remunerativo_display",
        "bruto_display",
        "descuentos_display",
        "neto_display",
        "contribuciones_display",
        "costo_laboral_display",
        "recibo_sueldo",
    )

    readonly_fields = (
        "detalle_link",
        "remunerativo_display",
        "no_remunerativo_display",
        "bruto_display",
        "descuentos_display",
        "neto_display",
        "contribuciones_display",
        "costo_laboral_display",
        "recibo_sueldo",
    )

    @admin.display(description="")
    def detalle_link(self, obj):
        if not obj.pk:
            return ""

        url = reverse(
            "admin:liquidacion_liquidacionempleado_change",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}">Ver detalle</a>',
            url,
        )

    @admin.display(description="Recibo")
    def recibo_sueldo(self, obj):
        if not obj or not obj.pk:
            return "-"

        return format_html(
            '{} {}',
            self._boton_recibo(obj, "original", "Original"),
            self._boton_recibo(obj, "duplicado", "Duplicado"),
        )

    def _boton_recibo(self, obj, tipo, etiqueta):
        url = reverse(
            "admin:liquidacionempleado_recibo",
            args=[obj.pk],
        )

        url = f"{url}?tipo={tipo}"
        filename = f"recibo-{obj.pk}-{tipo}.pdf"

        return format_html(
            '<a href="{}" target="_blank" '
            'class="button js-recibo-pdf" '
            'style="display: inline-block; margin-right: 4px;" '
            'data-url="{}" '
            'data-filename="{}">{}</a>',
            url,
            url,
            filename,
            etiqueta,
        )


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

    def response_change(self, request, obj):
        if "_txt" in request.POST:
            txt = LsdTxtArcaService(obj.id).generar()

            response = HttpResponse(
                txt,
                content_type="text/plain",
            )
            response["Content-Disposition"] = (
                f'attachment; filename="liquidacion_{normalizar_identificador(obj.empresa.nombre)}_{obj.periodo.strftime("%m_%Y")}_{obj.numero}.txt"'
            )

            return response

        return super().response_change(request, obj)
