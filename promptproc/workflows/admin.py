from django.contrib import admin
from .models import dag

############
class dagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    empty_value_display = '-empty-'
    
admin.site.register(dag, dagAdmin)
