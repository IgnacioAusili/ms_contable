from django.contrib import admin
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import path
from django.template.loader import render_to_string

from base_imponible.models import ResultadoBaseImponible
from plantilla_liquidacion.models import PlantillaLiquidacion
from .a_detalles_liquidacion import DetalleLiquidacionInline
from ..models import TramoSituacionRevista
from ..models.m_liquidacion_empleado import LiquidacionEmpleado
from ..models.m_detalles_liquidacion import DetalleLiquidacion
from ..forms.f_liquidacion_empleado import (
    LiquidacionEmpleadoForm, LiquidacionEmpleadoInlineForm,
    LiquidacionEmpleadoInlineFormSet,
    ResultadoBaseImponibleInlineForm, TramoSituacionRevistaInlineForm
)
from ..services.s_expresiones import LiquidacionEmpleadoService
from ..services.s_recibo import ReciboSueldoService


class TramoSituacionRevistaInline(admin.TabularInline):
    model = TramoSituacionRevista
    form = TramoSituacionRevistaInlineForm

    extra = 0
    max_num = 3
    can_delete = True
    show_change_link = True

    fields = (
        "situacion_revista",
        "dia_inicio",
    )

    readonly_fields = ("situacion_revista",)

    ordering = ("dia_inicio",)

    @admin.display(description="Situación de Revista")
    def situacion_revista(self, obj):
        return "Situación de Revista"


class ResultadoBaseImponibleInline(admin.TabularInline):
    model = ResultadoBaseImponible
    form = ResultadoBaseImponibleInlineForm

    extra = 0
    max_num = 0
    can_delete = False

    fields = ("base_imponible_display", "descripcion_display", "importe")

    readonly_fields = ("base_imponible_display", "descripcion_display")

    @admin.display(description="Base imponible")
    def base_imponible_display(self, obj):
        return obj.base_imponible

    @admin.display(description="Descripción")
    def descripcion_display(self, obj):
        return obj.base_imponible.descripcion


@admin.register(LiquidacionEmpleado)
class LiquidacionEmpleadoAdmin(admin.ModelAdmin):
    inlines = [TramoSituacionRevistaInline, DetalleLiquidacionInline, ResultadoBaseImponibleInline]
    form = LiquidacionEmpleadoForm

    fieldsets = (
        (None, {
            "fields": (
                "liquidacion",
                "empleado",
            ),
        }),
        ("Datos Adicionales", {
            "classes": ("columnas-custom",),
            "fields": (
                ("fecha_rubrica", "cantidad_dias_proporcionar_tope", "unidad_tiempo_trabajado", "tiempo_trabajado"),
                ("codigo_situacion", "codigo_condicion", "codigo_actividad",
                 "codigo_modalidad_contratacion", "codigo_siniestrado", "codigo_localidad"),
                ("porcentaje_aporte_adicional_ss", "porcentaje_contrib_tarea_diferencial",
                 "remuneracion_maternidad_anses"),
                ("cantidad_adherentes_obra_social", "aporte_adicional_obra_social", "contrib_adicional_obra_social"),
                ("base_calc_diferencial_aportes_obra_social_fsr", "base_calc_diferencial_contrib_obra_social_fsr",
                 "base_calc_diferencial_ley_riesgos_trabajo", "base_calc_diferencial_aportes_seg_social",
                 "base_calc_diferencial_contrib_seg_social")
            )
        }),
        ("Totales de liquidación", {
            "classes": ("columnas-custom",),  # "totales-liquidacion",),
            "fields": (
                ("remunerativo_display", "bruto_display", "descuentos_display",),
                ("no_remunerativo_display", "neto_display", "contribuciones_display",),
                ("costo_laboral_display",),
            ),
        }),
        ("Observaciones", {
            "fields": ("observaciones",),
        }),
    )

    readonly_fields = (
        "liquidacion",
        "empleado",
        "remunerativo_display",
        "no_remunerativo_display",
        "bruto_display",
        "descuentos_display",
        "neto_display",
        "contribuciones_display",
        "costo_laboral_display",
    )

    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Remunerativo:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["remunerativo"]}</small>'
    #     )
    # )
    # def remunerativo_display(self, obj):
    #     return obj.remunerativo_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">No Remunerativo:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["no_remunerativo"]}</small>'
    #     )
    # )
    # def no_remunerativo_display(self, obj):
    #     return obj.no_remunerativo_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Bruto:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["bruto"]}</small>'
    #     )
    # )
    # def bruto_display(self, obj):
    #     return obj.bruto_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Descuentos:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["descuentos"]}</small>'
    #     )
    # )
    # def descuentos_display(self, obj):
    #     return obj.descuentos_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Neto:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["neto"]}</small>'
    #     )
    # )
    # def neto_display(self, obj):
    #     return obj.neto_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Contribuciones:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["contribuciones"]}</small>'
    #     )
    # )
    # def contribuciones_display(self, obj):
    #     return obj.contribuciones_display
    #
    # @admin.display(
    #     description=format_html(
    #         '<span class="nombre-campo">Costo Laboral:</span>'
    #         f'<small class="identificador-campo">{IDENTIFICADORES_LE["costo_laboral"]}</small>'
    #     )
    # )
    # def costo_laboral_display(self, obj):
    #     return obj.costo_laboral_display

    change_form_template = "admin/liquidacion/change_form.html"

    # Ocultar LiquidacionEmpleado de las vistas globales
    def has_module_permission(self, request):
        return False

    class Media:
        js = ("liquidacion/admin/detalle_liquidacion_empleado.js",)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None, ):
        extra_context = extra_context or {}

        if object_id:
            obj = self.get_object(request, object_id)

            recibo_url = reverse(
                "admin:liquidacionempleado_recibo",
                args=[obj.pk],
            )

            if obj:
                extra_context["liquidacion_empleado"] = True
                extra_context["plantillas"] = (
                    PlantillaLiquidacion.objects
                    .filter(empresa=obj.liquidacion.empresa)
                    .order_by("denominacion")
                )

                extra_context["recibo_original_url"] = (
                    f"{recibo_url}?tipo=original"
                )
                extra_context["recibo_duplicado_url"] = (
                    f"{recibo_url}?tipo=duplicado"
                )

        return super().changeform_view(request, object_id, form_url, extra_context, )

    def get_urls(self):
        urls = super().get_urls()

        custom = [
            path(
                "<int:object_id>/recibo/",
                self.admin_site.admin_view(self.recibo_view),
                name="liquidacionempleado_recibo",
            ),
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

    def recibo_view(self, request, object_id):
        tipo = request.GET.get("tipo", "original")

        datos = ReciboSueldoService(
            LiquidacionEmpleado.objects.get(pk=object_id)
        ).obtener_datos(tipo=tipo)

        html = render_to_string(
            "admin/liquidacion/recibo_sueldo.html",
            datos,
            request=request,
        )

        return HttpResponse(
            html,
            content_type="text/html",
        )

    def plantilla_detalles_view(self, request, plantilla_id):
        plantilla = get_object_or_404(
            PlantillaLiquidacion,
            pk=plantilla_id,
        )

        detalles = [
            {
                "concepto": detalle.concepto.versiones.ultima().id,
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
            return JsonResponse(
                {"identificador": "", "grupo": "", "tipo": "", "categoria": "", "unidad": "", }
            )

        return JsonResponse({
            "identificador": concepto.identificador,
            "grupo": concepto.grupo.denominacion if concepto.grupo else "",
            "tipo": concepto.get_tipo_display(),
            "categoria": concepto.get_categoria_display(),
            "unidad": concepto.get_unidad_display(),
        })


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
