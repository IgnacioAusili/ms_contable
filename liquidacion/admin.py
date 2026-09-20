from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from .models import Liquidacion, LiquidacionEmpleado, DetalleLiquidacion
from .forms import LiquidacionForm, LiquidacionEmpleadoInlineForm, LiquidacionEmpleadoInlineFormSet, DetalleLiquidacionForm, DetalleLiquidacionFormSet


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
        "banco_de_cobro",
        "categoria",
        "remunerativo",
        "no_remunerativo",
        "bruto",
        "descuentos",
        "neto",
        "contribuciones",
        "costo_laboral",
    )

    readonly_fields = (
        "detalle_link",
        "banco_de_cobro",
        "categoria",
        "remunerativo",
        "no_remunerativo",
        "bruto",
        "descuentos",
        "neto",
        "contribuciones",
        "costo_laboral",
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


@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    form = LiquidacionForm
    inlines = [LiquidacionEmpleadoInline]
    actions = None

    list_display = (
        "empresa",
        "periodo",
        "fecha_pago",
        "estado",
        "domicilio_empresa"
    )
    list_select_related = ('empresa',)

    list_filter = ('empresa', 'estado',)

    change_form_template = "admin/liquidacion/liquidacion/change_form.html"


class DetalleLiquidacionInline(admin.TabularInline):
    model = DetalleLiquidacion
    form = DetalleLiquidacionForm
    formset = DetalleLiquidacionFormSet

    extra = 0
    can_delete = True
    show_change_link = True

    fields = (
        "concepto",
        "unidad",
        "unidades",
        "expresion_base",
        "base",
        "importe",
    )

    readonly_fields = (
        "unidad",
        "base",
        "importe",
    )

    @admin.display(description="Unidad")
    def unidad(self, obj):
        texto = "-"

        if obj and obj.pk and obj.concepto_id:
            texto = obj.concepto.get_unidad_display()

        return format_html('<span class="unidad-display">{}</span>', texto)


@admin.register(LiquidacionEmpleado)
class LiquidacionEmpleadoAdmin(admin.ModelAdmin):
    inlines = [DetalleLiquidacionInline]

    fields = (
        "liquidacion",
        "empleado",
        "banco_de_cobro",
        "categoria",
        "remunerativo",
        "no_remunerativo",
        "bruto",
        "descuentos",
        "neto",
        "contribuciones",
        "costo_laboral",
    )

    readonly_fields = fields

    change_form_template = "admin/liquidacion/liquidacion/change_form.html"

    # Ocultar LiquidacionEmpleado de las vistas globales
    def has_module_permission(self, request):
        return False

    class Media:
        js = ("liquidacion/admin/detalle_liquidacion.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "concepto-unidad/<int:concepto_id>/",
                self.admin_site.admin_view(self.concepto_unidad_view),
                name="liquidacion_concepto_unidad",
            ),
        ]
        return custom + urls

    def concepto_unidad_view(self, request, concepto_id):
        VersionConceptoModel = DetalleLiquidacion._meta.get_field("concepto").related_model

        try:
            concepto = VersionConceptoModel.objects.get(pk=concepto_id)
        except VersionConceptoModel.DoesNotExist:
            return JsonResponse({"unidad": ""})

        return JsonResponse({"unidad": concepto.get_unidad_display()})
