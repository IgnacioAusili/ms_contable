from django.contrib import admin
from django.utils.html import format_html

from concepto.choices import Unidad
from concepto.models import VersionConcepto
from ..models.m_detalles_liquidacion import DetalleLiquidacion
from ..forms.f_detalles_liquidacion import DetalleLiquidacionForm, DetalleLiquidacionFormSet


class DetalleLiquidacionInline(admin.StackedInline):
    model = DetalleLiquidacion
    form = DetalleLiquidacionForm
    formset = DetalleLiquidacionFormSet

    extra = 0
    can_delete = True
    show_change_link = True

    fieldsets = (
        (
            "Concepto",
            {
                "classes": ("columnas-custom",),
                "fields": (
                    ("concepto", "grupo", "tipo", "categoria",),
                    ("unidad", "unidades", "formula_base",),
                    ("base_display", "importe_display",),
                ),
            },
        ),
        (
            "Detalles Registro 03 LSD Arca",
            {
                "classes": ("columnas-custom", "registro03-fieldset", ),
                "fields": (
                    ("cantidad", "unidades_lsd", "debito_credito", "periodo_ajuste_retroactivo"),
                ),
            },
        ),
    )

    readonly_fields = (
        "grupo",
        "tipo",
        "categoria",
        "unidad",
        "base_display",
        "importe_display",
    )

    @admin.display(description="Grupo")
    def grupo(self, obj):
        texto = "-"

        if obj and obj.pk and obj.concepto_id:
            texto = obj.concepto.grupo.denominacion if obj.concepto.grupo else "-"

        return format_html('<span class="grupo-display">{}</span>', texto)

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
        nombre = "-"
        descripcion = ""

        if obj and obj.pk and obj.concepto_id:
            nombre = obj.concepto.get_unidad_display()
            descripcion = Unidad(obj.concepto.unidad).descripcion

        return format_html(
            '<span class="unidad-display" title="{}">{}</span>',
            descripcion,
            nombre,
        )
