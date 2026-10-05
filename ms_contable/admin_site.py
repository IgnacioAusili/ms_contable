from urllib.parse import unquote

from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.http import Http404
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
                model_urls = []
                for pattern in url.url_patterns:
                    route = getattr(pattern.pattern, "_route", None)
                    model_admin = getattr(pattern.callback, "model_admin", None)
                    callback = pattern.callback
                    if model_admin is not None and "<path:object_id>" in (route or ""):
                        callback = self.admin_view(
                            self._missing_object_404_view(callback, model_admin)
                        )
                        pattern = path(
                            route, callback, pattern.default_args, name=pattern.name
                        )
                    model_urls.append(pattern)
                custom_urls.append(path(f"{slug}/", include(model_urls)))
            else:
                custom_urls.append(url)

        return custom_urls

    def _missing_object_404_view(self, view, model_admin):
        def show_not_found(request, object_id, *args, **kwargs):
            if (
                model_admin.has_view_or_change_permission(request)
                or model_admin.has_delete_permission(request)
            ) and model_admin.get_object(request, unquote(object_id)) is None:
                raise Http404
            return view(request, object_id, *args, **kwargs)

        return show_not_found
