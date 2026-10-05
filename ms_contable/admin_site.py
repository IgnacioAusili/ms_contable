from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.urls import include, path
from django.urls.resolvers import URLResolver


class MSContableAdminConfig(AdminConfig):
    default_site = "ms_contable.admin_site.MSContableAdminSite"


class MSContableAdminSite(AdminSite):
    model_route_slugs = {
        ("admin", "logentry"): "registro-de-actividad",
        ("base_imponible", "baseimponible"): "bases-imponibles",
        ("categoria_laboral", "categorialaboral"): "categorias-laborales",
        ("concepto", "concepto"): "conceptos",
        ("empleado", "empleado"): "empleados",
        ("empresa", "empresa"): "empresas",
        ("grupo_concepto", "grupoconcepto"): "grupos-de-conceptos",
        ("liquidacion", "liquidacion"): "liquidaciones",
        ("liquidacion", "liquidacionempleado"): "liquidaciones-por-empleado",
        ("plantilla_liquidacion", "plantillaliquidacion"): "plantillas-de-liquidacion",
    }

    def app_index(self, request, app_label, extra_context=None):
        if app_label == "admin":
            extra_context = {
                **(extra_context or {}),
                "title": "Registro de actividad",
            }
        return super().app_index(request, app_label, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        route_slugs = {
            f"{app_label}/{model_name}/": slug
            for (app_label, model_name), slug in self.model_route_slugs.items()
        }
        custom_urls = []

        for url in urls:
            route = getattr(getattr(url, "pattern", None), "_route", None)
            slug = route_slugs.get(route)
            if isinstance(url, URLResolver) and slug:
                custom_urls.append(path(f"{slug}/", include(url.url_patterns)))
            else:
                custom_urls.append(url)

        return custom_urls
