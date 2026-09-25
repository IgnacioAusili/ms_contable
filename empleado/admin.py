from django.contrib import admin
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import path
from categoria_laboral.models import CategoriaLaboral
from .forms import EmpleadoAdminForm
from .models import Empleado, VersionEmpleado
from .services import actualizar_empleado


class VersionEmpleadoInline(admin.TabularInline):
    model = VersionEmpleado

    can_delete = False
    max_num = 0
    extra = 0

    verbose_name = "Versión anterior"
    verbose_name_plural = "Historial de versiones"

    fields = (
        "version",
        "conyuge",
        "cantidad_hijos",
        "codigo_obra_social",
        "categoria_laboral",
        "dependencia_revista",
        "banco_de_cobro",
        "cbu",
        "forma_de_pago",
        "cct",
        "cobertura_scvo",
        "corresponde_reduccion",
    )

    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).order_by("-version")


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    form = EmpleadoAdminForm
    inlines = [VersionEmpleadoInline]

    list_display = (
        'cuil_display',
        'apellidos',
        'nombres',
        'empresa',
        'legajo',
        'fecha_ingreso',
    )
    list_per_page = 25

    list_select_related = ('empresa',)

    search_fields = ('cuil_display', 'apellidos')
    search_help_text = "Buscar por apellido o cuil"

    list_filter = ('empresa',)

    change_form_template = "admin/empleado/change_form.html"

    class Media:
        js = ("empleado/admin/crear_empleado.js",)

    def _version_vigente(self, obj):
        return (
            obj.ultima_version[0]  # Prefetch(..., ) siempre devuelve una colección
            if obj.ultima_version
            else None
        )

    def get_queryset(self, request):
        queryset = self.model.objects.all()

        # queryset = queryset.activos()
        versiones = VersionEmpleado.objects.ultima_version()

        return queryset.prefetch_related(
            Prefetch(
                "versiones",
                queryset=versiones,
                to_attr="ultima_version",
            )
        )

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        actualizar_empleado(
            empleado=obj,
            dependencia_revista=form.cleaned_data["dependencia_revista"],
            categoria_laboral=form.cleaned_data["categoria_laboral"],
            conyuge=form.cleaned_data["conyuge"],
            cantidad_hijos=form.cleaned_data["cantidad_hijos"],
            banco_de_cobro=form.cleaned_data["banco_de_cobro"],
            cbu=form.cleaned_data["cbu"],
            forma_de_pago=form.cleaned_data["forma_de_pago"],
            cct=form.cleaned_data["cct"],
            cobertura_scvo=form.cleaned_data["cobertura_scvo"],
            corresponde_reduccion=form.cleaned_data["corresponde_reduccion"],
            codigo_obra_social=form.cleaned_data["codigo_obra_social"],
        )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "categorias-por-empresa/<int:empresa_id>/",
                self.admin_site.admin_view(
                    self.categorias_por_empresa_view
                ),
                name="empleado_categorias_por_empresa",
            ),
        ]

        return custom_urls + urls

    def categorias_por_empresa_view(self, request, empresa_id):
        categorias = (
            CategoriaLaboral.objects
            .filter(empresa_id=empresa_id)
            .order_by("denominacion")
        )

        return JsonResponse({
            "categorias": [
                {
                    "id": categoria.pk,
                    "nombre": str(categoria),
                }
                for categoria in categorias
            ]
        })
