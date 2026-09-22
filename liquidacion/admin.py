from django.contrib import admin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import path
from plantilla_liquidacion.models import PlantillaLiquidacion
from .models import Liquidacion, LiquidacionEmpleado, DetalleLiquidacion
from .forms import LiquidacionForm, LiquidacionEmpleadoInlineForm, LiquidacionEmpleadoInlineFormSet, DetalleLiquidacionForm, DetalleLiquidacionFormSet
from .services.s_expresiones import LiquidacionEmpleadoService


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
        "__str__",
        "periodo",
        "fecha_pago",
        "estado",
        "domicilio_empresa"
    )
    list_select_related = ('empresa',)

    list_filter = ('empresa', 'estado',)

    search_fields = ('periodo',)
    search_help_text = "Busqueda por periodo (fecha, año, mes, etc)"

    ordering = ('empresa', 'periodo',)

    change_form_template = "admin/liquidacion/change_form.html"


class DetalleLiquidacionInline(admin.TabularInline):
    model = DetalleLiquidacion
    form = DetalleLiquidacionForm
    formset = DetalleLiquidacionFormSet

    extra = 0
    can_delete = True
    show_change_link = True

    fields = (
        "concepto",
        "tipo",
        "categoria",
        "unidad",
        "unidades",
        "formula_base",
        "base",
        "importe",
    )

    readonly_fields = (
        "tipo",
        "categoria",
        "unidad",
        "base",
        "importe",
    )

    @admin.display(description="Tipo")
    def tipo(self, obj):
        texto = "-"

        if obj and obj.pk and obj.concepto_id:
            texto = obj.concepto.get_tipo_display()

        return format_html('<span class="tipo-display">{}</span>', texto)

    @admin.display(description="Categoria")
    def categoria(self, obj):
        texto = "-"

        if obj and obj.pk and obj.concepto_id:
            texto = obj.concepto.get_categoria_display()

        return format_html('<span class="categoria-display">{}</span>', texto)

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

    change_form_template = "admin/liquidacion/change_form.html"

    # Ocultar LiquidacionEmpleado de las vistas globales
    def has_module_permission(self, request):
        return False

    class Media:
        js = ("liquidacion/admin/detalle_liquidacion.js",)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None,):
        extra_context = extra_context or {}

        if object_id:
            obj = self.get_object(request, object_id)

            if obj:
                extra_context["liquidacion_empleado"] = True
                extra_context["plantillas"] = (
                    PlantillaLiquidacion.objects
                    .filter(empresa=obj.liquidacion.empresa)
                    .order_by("denominacion")
                )

        return super().changeform_view(request, object_id, form_url, extra_context,)

    def get_urls(self):
        urls = super().get_urls()

        custom = [
            path(
                "plantilla/<int:plantilla_id>/detalles/",
                self.admin_site.admin_view(self.plantilla_detalles_view),
                name="liquidacion_plantilla_detalles",
            ),
            path(
                "concepto-detalles/<int:concepto_id>/",
                self.admin_site.admin_view(self.concepto_detalles_view),
                name="liquidacion_concepto_detalles",
            ),
        ]

        return custom + urls

    def response_change(self, request, obj):
        if "_calcular" in request.POST:
            LiquidacionEmpleadoService(obj).liquidar()
            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def plantilla_detalles_view(self, request, plantilla_id):
        plantilla = get_object_or_404(
            PlantillaLiquidacion,
            pk=plantilla_id,
        )

        detalles = [
            {
                "concepto": detalle.concepto_id,
                "unidades": str(detalle.unidades),
                "formula_base": detalle.formula_base,
            }
            for detalle in plantilla.detalles.all()
        ]

        return JsonResponse({"detalles": detalles})

    def concepto_detalles_view(self, request, concepto_id):
        VersionConceptoModel = DetalleLiquidacion._meta.get_field("concepto").related_model

        try:
            concepto = VersionConceptoModel.objects.get(pk=concepto_id)
        except VersionConceptoModel.DoesNotExist:
            return JsonResponse({
                "tipo": "", "categoria": "", "unidad": "",
            })

        return JsonResponse({
            "tipo": concepto.get_tipo_display(),
            "categoria": concepto.get_categoria_display(),
            "unidad": concepto.get_unidad_display(),
        })
