from django.contrib import admin
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from django.db.models import Prefetch
from concepto.models import VersionConcepto
from liquidacion.models import DetalleLiquidacion
from .models import PlantillaLiquidacion, DetallePlantillaLiquidacion
from .forms import DetallePlantillaLiquidacionForm


class DetallePlantillaLiquidacionInline(admin.TabularInline):
    model = DetallePlantillaLiquidacion
    form = DetallePlantillaLiquidacionForm

    extra = 0
    can_delete = True
    show_change_link = True

    fields = (
        "concepto",
        "grupo",
        "tipo",
        "categoria",
        "unidad",
        "unidades",
        "formula_base",
    )

    readonly_fields = (
        "grupo",
        "tipo",
        "categoria",
        "unidad",
    )

    @admin.display(description="Grupo")
    def grupo(self, obj):
        version = self.version_vigente(obj)

        texto = (
            version.grupo.denominacion
            if version and version.grupo
            else "-"
        )

        return format_html('<span class="grupo-display">{}</span>', texto)

    @admin.display(description="Tipo")
    def tipo(self, obj):
        version = self.version_vigente(obj)

        texto = version.get_tipo_display() if version else "-"

        return format_html('<span class="tipo-display">{}</span>', texto)

    @admin.display(description="Categoria")
    def categoria(self, obj):
        version = self.version_vigente(obj)

        texto = version.get_categoria_display() if version else "-"

        return format_html('<span class="categoria-display">{}</span>', texto)

    @admin.display(description="Unidad")
    def unidad(self, obj):
        nombre = "-"
        descripcion = ""

        version = self.version_vigente(obj)

        if version:
            unidad = VersionConcepto.Unidad(version.unidad)
            nombre = unidad.label
            descripcion = unidad.descripcion

        return format_html(
            '<span class="unidad-display" title="{}">{}</span>',
            descripcion,
            nombre,
        )

    def version_vigente(self, obj):
        if not obj or not obj.concepto_id:
            return None

        versiones = getattr(
            obj.concepto,
            "_versiones_vigentes",
            [],
        )

        return versiones[0] if versiones else None

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        versiones = (
            VersionConcepto.todos
            .select_related("grupo")
            .ultima_version()
        )

        return (
            queryset
            .select_related("concepto")
            .prefetch_related(
                Prefetch(
                    "concepto__versiones",
                    queryset=versiones,
                    to_attr="_versiones_vigentes",
                )
            )
        )


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
            return JsonResponse(
                {"identificador": "", "grupo": "", "tipo": "", "categoria": "", "unidad": "",}
            )

        return JsonResponse({
            "identificador": concepto.identificador,
            "grupo": concepto.grupo.denominacion if concepto.grupo else "",
            "tipo": concepto.get_tipo_display(),
            "categoria": concepto.get_categoria_display(),
            "unidad": concepto.get_unidad_display(),
        })
