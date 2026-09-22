from django.contrib import admin
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from liquidacion.models import DetalleLiquidacion
from .models import PlantillaLiquidacion, DetallePlantillaLiquidacion
from .forms import DetallePlantillaLiquidacionForm, DetallePlantillaLiquidacionFormSet


class DetallePlantillaLiquidacionInline(admin.TabularInline):
    model = DetallePlantillaLiquidacion
    form = DetallePlantillaLiquidacionForm
    formset = DetallePlantillaLiquidacionFormSet

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
    )

    readonly_fields = (
        "tipo",
        "categoria",
        "unidad",
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


@admin.register(PlantillaLiquidacion)
class PlantillaLiquidacionAdmin(admin.ModelAdmin):
    inlines = [DetallePlantillaLiquidacionInline]

    list_per_page = 10
    list_display = ('denominacion', 'empresa',)
    list_filter = ('empresa',)
    search_fields = ('denominacion',)
    search_help_text = "Buscar por denominacion"
    preserve_filters = True
    list_select_related = ('empresa',)
    ordering = ('denominacion', 'empresa',)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("empresa",)

        return ()

    change_form_template = "admin/plantilla_liquidacion/change_form.html"

    class Media:
        js = ("plantilla_liquidacion/admin/detalle_plantilla_liquidacion.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "concepto-detalles/<int:concepto_id>/",
                self.admin_site.admin_view(self.concepto_detalles_view),
                name="liquidacion_concepto_detalles",
            ),
        ]
        return custom + urls

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
