from django.contrib import admin
from base_imponible.models import BaseImponible


@admin.register(BaseImponible)
class BaseImponibleAdmin(admin.ModelAdmin):
    list_display = (
        "identificador",
        "denominacion",
        "descripcion",
    )
    ordering = ('denominacion',)
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
