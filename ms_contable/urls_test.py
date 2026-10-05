from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView


admin.site.site_header = settings.APP_NAME
admin.site.site_title = settings.APP_NAME
admin.site.index_title = "Panel de Administración"


urlpatterns = [
    path("", RedirectView.as_view(url="/test/", permanent=False)),
    path("test/", admin.site.urls),
]
