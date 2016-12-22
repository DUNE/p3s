from django.contrib import admin
from .models import dataset, datatype

############
class datasetAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'state', 'comment', 'datatype', 'wf', 'wfuuid',)
    empty_value_display = '-empty-'
    
admin.site.register(dataset, datasetAdmin)

class datatypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'comment',)
    empty_value_display = '-empty-'
    
admin.site.register(datatype, datatypeAdmin)

