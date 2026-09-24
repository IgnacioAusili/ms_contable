from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from categoria_laboral.models import CategoriaLaboral
from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ('cuil_display', 'apellidos', 'nombres', 'empresa', 'categoria_laboral', 'legajo', 'fecha_ingreso', 'banco_de_cobro')
    list_select_related = ('empresa', 'categoria_laboral',)
    search_fields = ('cuil_display','apellidos')
    search_help_text = "Buscar por apellido o cuil"
    list_filter = ('empresa',)
    list_editable = ('banco_de_cobro',)
    list_display_links = None

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.method == "POST":
            pass
        elif obj is not None:
            # Al editar un empleado existente
            form.base_fields["categoria_laboral"].queryset = (
                CategoriaLaboral.objects.filter(
                    empresa=obj.empresa
                )
            )
        else:
            # Al crear: todavía no hay empresa seleccionada
            form.base_fields["categoria_laboral"].queryset = (
                CategoriaLaboral.objects.none()
            )

        return form

    class Media:
        js = ("empleado/admin/crear_empleado.js",)

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
