from django.contrib import admin
from .models import job

class jobAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'state', 'ts_def', 'ts_dispatch', 'ts_start', 'ts_stop')
    empty_value_display = '-empty-'
    
admin.site.register(job, jobAdmin)

# Register your models here.
