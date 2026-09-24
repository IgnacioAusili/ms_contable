from django.contrib import admin, messages
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path, reverse
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from concepto.models import VersionConcepto, Concepto
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

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        empresa = obj.empresa if obj else None

        if empresa:
            formset.form.base_fields["concepto"].queryset = (
                Concepto.objects
                .filter(empresa=empresa)
            )

        return formset

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
    list_display = ('denominacion', 'empresa', 'duplicar',)
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

    @admin.display(description="Duplicar")
    def duplicar(self, obj):
        url = reverse(
            "admin:plantillaliquidacion_duplicar",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}">Duplicar</a>',
            url,
        )

    def response_change(self, request, obj):
        if "_agregar_todos" in request.POST:
            conceptos_existentes = set(
                obj.detalles.values_list("concepto_id", flat=True)
            )

            conceptos = (
                Concepto.objects
                .filter(empresa=obj.empresa)
                .exclude(pk__in=conceptos_existentes)
            )

            detalles = [
                DetallePlantillaLiquidacion(
                    plantilla=obj,
                    concepto=concepto,
                    unidades=1,
                    formula_base="0",
                )
                for concepto in conceptos
            ]

            DetallePlantillaLiquidacion.objects.bulk_create(detalles)

            self.message_user(
                request,
                f"Se agregaron {len(detalles)} conceptos a la plantilla.",
                messages.SUCCESS,
            )

            return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "concepto-detalles/<int:concepto_id>/",
                self.admin_site.admin_view(self.concepto_detalles_view),
                name="liquidacion_concepto_detalles",
            ),
            path(
                "<int:object_id>/duplicar/",
                self.admin_site.admin_view(self.duplicar_view),
                name="plantillaliquidacion_duplicar",
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

    def duplicar_view(self, request, object_id):
        plantilla = self.get_object(request, object_id)

        if plantilla is None:
            self.message_user(
                request,
                "La plantilla no existe.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(
                reverse("admin:plantilla_liquidacion_plantillaliquidacion_changelist")
            )

        denominacion = self._denominacion_duplicada(plantilla)

        nueva_plantilla = PlantillaLiquidacion.objects.create(
            empresa=plantilla.empresa,
            denominacion=denominacion,
        )

        detalles = [
            DetallePlantillaLiquidacion(
                plantilla=nueva_plantilla,
                concepto=detalle.concepto,
                unidades=detalle.unidades,
                formula_base=detalle.formula_base,
            )
            for detalle in plantilla.detalles.all()
        ]

        DetallePlantillaLiquidacion.objects.bulk_create(detalles)

        self.message_user(
            request,
            f'Se duplicó la plantilla "{plantilla.denominacion}".',
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(
            reverse(
                "admin:plantilla_liquidacion_plantillaliquidacion_change",
                args=[nueva_plantilla.pk],
            )
        )

    def _denominacion_duplicada(self, plantilla):
        base = f"{plantilla.denominacion} (copia)"

        denominaciones = set(
            PlantillaLiquidacion.objects
            .filter(
                empresa=plantilla.empresa,
                denominacion__startswith=base,
            )
            .values_list("denominacion", flat=True)
        )

        if base not in denominaciones:
            return base

        numero = 2

        while f"{base} {numero}" in denominaciones:
            numero += 1

        return f"{base}".replace("copia", f"copia {numero}")
