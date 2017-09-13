from django.contrib import admin
from .models import pur

############
class purAdmin(admin.ModelAdmin):
    list_display = ('run', 'tpc', 'ts', 'lifetime', 'error', 'count')
    empty_value_display = '-empty-'
    
admin.site.register(pur, purAdmin)

