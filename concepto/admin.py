from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from django.db.models import Prefetch
from .models import Concepto, VersionConcepto
from .forms import ConceptoAdminForm
from .services import actualizar_concepto


class VersionConceptoInline(admin.TabularInline):
    model = VersionConcepto
    extra = 0
    can_delete = False

    fields = (
        "version",
        "denominacion",
        "grupo",
        "codigo_arca",
        "categoria",
        "tipo",
        "unidad",
    )

    readonly_fields = fields


@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    form = ConceptoAdminForm
    inlines = [VersionConceptoInline]
    actions = None

    list_display = (
        "id",
        "empresa",
        "denominacion",
        "grupo",
        "codigo_arca",
        "categoria",
        "tipo",
        "unidad",
    )

    def _version_vigente(self, obj):
        return (
            obj.versiones_ordenadas[0]
            if obj.versiones_ordenadas
            else None
        )

    @admin.display(description="Denominación")
    def denominacion(self, obj):
        version = self._version_vigente(obj)
        return version.denominacion if version else "-"

    @admin.display(description="Código ARCA")
    def codigo_arca(self, obj):
        version = self._version_vigente(obj)
        return version.codigo_arca if version else "-"

    @admin.display(description="Categoría")
    def categoria(self, obj):
        version = self._version_vigente(obj)
        return version.get_categoria_display() if version else "-"

    @admin.display(description="Tipo")
    def tipo(self, obj):
        version = self._version_vigente(obj)
        return version.get_tipo_display() if version else "-"

    @admin.display(description="Unidad")
    def unidad(self, obj):
        version = self._version_vigente(obj)
        return version.get_unidad_display() if version else "-"

    @admin.display(description="Grupo")
    def grupo(self, obj):
        version = self._version_vigente(obj)
        return version.grupo if version else "-"

    def get_queryset(self, request):
        versiones = (
            VersionConcepto.objects
            .order_by("-version")
        )

        return (
            super()
            .get_queryset(request)
            .activos()
            .prefetch_related(
                Prefetch(
                    "versiones",
                    queryset=versiones,
                    to_attr="versiones_ordenadas",
                )
            )
        )

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        actualizar_concepto(
            concepto=obj,
            denominacion=form.cleaned_data["denominacion"],
            codigo_arca=form.cleaned_data["codigo_arca"],
            categoria=form.cleaned_data["categoria"],
            tipo=form.cleaned_data["tipo"],
            unidad=form.cleaned_data["unidad"],
            grupo=form.cleaned_data["grupo"],
        )

    def delete_view(self, request, object_id, extra_context=None):
        concepto = self.get_object(request, object_id)

        if concepto is not None:
            concepto.eliminado = True
            concepto.save(update_fields=["eliminado"])

        return redirect(
            reverse(
                f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
            )
        )
