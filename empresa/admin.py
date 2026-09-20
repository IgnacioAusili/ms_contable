from django.contrib import admin
from .models import Empresa
from django.contrib.auth.models import Group, User


admin.site.register(Empresa)

admin.site.unregister(Group)
admin.site.unregister(User)
