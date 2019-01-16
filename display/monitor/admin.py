from django.contrib import admin
from .models import monrun

############
class monrunAdmin(admin.ModelAdmin):
    list_display = ('pk', 'run', 'subrun', 'directory', 'dl', 'ts', 'jobtype', 'summary', 'description')
    empty_value_display = '-empty-'
    
admin.site.register(monrun, monrunAdmin)
