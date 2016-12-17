from django.contrib import admin
from .models import dag, dagEdge, dagVertex
from .models import workflow, wfEdge, wfVertex

####################### DAG #############################    
class dagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'nvertices', 'root', 'ts_def')
    empty_value_display = '-empty-'
    
admin.site.register(dag, dagAdmin)
#--------------------------------------------------------
class dagVertexAdmin(admin.ModelAdmin):
    list_display = ('dag', 'name',)
    empty_value_display = '-empty-'
    
admin.site.register(dagVertex, dagVertexAdmin)
#--------------------------------------------------------
class dagEdgeAdmin(admin.ModelAdmin):
    list_display = ('dag', 'name', 'source', 'target',)
    empty_value_display = '-empty-'
    
admin.site.register(dagEdge, dagEdgeAdmin)

######################## WF #############################    
class workflowAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid','dag', 'description', 'ts_def',)
    empty_value_display = '-empty-'
    
admin.site.register(workflow, workflowAdmin)
#--------------------------------------------------------
class wfVertexAdmin(admin.ModelAdmin):
    list_display = ('name', 'wf', 'wfuuid',)
    empty_value_display = '-empty-'
    
admin.site.register(wfVertex, wfVertexAdmin)
#--------------------------------------------------------
class wfEdgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'target', 'wf', 'wfuuid',)
    empty_value_display = '-empty-'
    
admin.site.register(wfEdge, wfEdgeAdmin)
