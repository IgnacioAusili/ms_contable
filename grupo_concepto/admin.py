from django.contrib import admin
from django.db.models import Case, When, Value, IntegerField
import json
from .models import GrupoConcepto, GRUPOS_PROTEGIDOS


@admin.register(GrupoConcepto)
class GrupoConceptoAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ('denominacion', 'codigo',)
    search_fields = ('denominacion', 'codigo',)
    list_display_links = None

    change_list_template = "admin/grupo_concepto/change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["grupos_protegidos"] = json.dumps(
            list(GRUPOS_PROTEGIDOS)
        )

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            grupo_obligatorio=Case(
                When(
                    codigo__in=GRUPOS_PROTEGIDOS,
                    then=Value(0),
                ),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "grupo_obligatorio",
            "denominacion",
        )
