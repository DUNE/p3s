from django.contrib import admin
from .models import job, stage

############
class jobAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'stage', 'priority', 'state', 'ts_def', 'ts_dispatch', 'ts_start', 'ts_stop')
    empty_value_display = '-empty-'
    
admin.site.register(job, jobAdmin)

############
class stageAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'njobs')
    empty_value_display = '-empty-'
    
admin.site.register(stage, stageAdmin)

