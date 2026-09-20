from django.contrib import admin
from .models import GrupoConcepto


@admin.register(GrupoConcepto)
class GrupoConceptoAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ('denominacion',)
    search_fields = ('denominacion',)
    list_display_links = None
