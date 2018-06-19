from django.contrib import admin
from .models import monrun

############
class monrunAdmin(admin.ModelAdmin):
    list_display = ('run', 'subrun', 'summary')
    empty_value_display = '-empty-'
    
admin.site.register(monrun, monrunAdmin)
