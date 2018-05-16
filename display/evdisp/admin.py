from django.contrib import admin
from .models import evdisp

############
class evdispAdmin(admin.ModelAdmin):
    list_display = ('run', 'subrun', 'evnum', 'changroup', 'datatype', 'ts', 'path')
    empty_value_display = '-empty-'
    
admin.site.register(evdisp, evdispAdmin)

