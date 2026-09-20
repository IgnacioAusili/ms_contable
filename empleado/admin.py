from django.contrib import admin
from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_per_page = 25
    list_display = ('cuil', 'apellidos', 'nombres', 'legajo', 'fecha_ingreso', 'banco_de_cobro')
    search_fields = ('cuil','apellidos')
    search_help_text = "Buscar por apellido o cuil"
    list_filter = ('empresa',)
    list_editable = ('banco_de_cobro',)
    list_display_links = None
