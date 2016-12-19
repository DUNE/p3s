from django.contrib import admin
from .models import job, jobtype, prioritypolicy

############
class jobAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'p_uuid', 'jobtype', 'payload', 'priority', 'state', 'ts_def', 'ts_dis', 'ts_sta', 'ts_sto')
    empty_value_display = '-empty-'
    
admin.site.register(job, jobAdmin)

############
class jobtypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'njobs')
    empty_value_display = '-empty-'
    
admin.site.register(jobtype, jobtypeAdmin)

############
class prioritypolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    empty_value_display = '-empty-'
    
admin.site.register(prioritypolicy, prioritypolicyAdmin)

