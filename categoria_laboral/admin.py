from django.contrib import admin
from .models import CategoriaLaboral


@admin.register(CategoriaLaboral)
class CategoriaLaboralAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('empresa', 'denominacion',)
    list_filter = ('empresa',)
    preserve_filters = True
    list_select_related = ('empresa',)
    list_editable = ('denominacion',)
    list_display_links = None
    ordering = ('empresa','denominacion',)
