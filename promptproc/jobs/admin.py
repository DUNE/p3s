from django.contrib import admin
from .models import job, stage, prioritypolicy

############
class jobAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'p_uuid', 'stage', 'priority', 'state', 'ts_def', 'ts_dis', 'ts_sta', 'ts_sto')
    empty_value_display = '-empty-'
    
admin.site.register(job, jobAdmin)

############
class stageAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'njobs')
    empty_value_display = '-empty-'
    
admin.site.register(stage, stageAdmin)

############
class prioritypolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    empty_value_display = '-empty-'
    
admin.site.register(prioritypolicy, prioritypolicyAdmin)

