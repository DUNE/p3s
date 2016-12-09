from django.contrib import admin
from .models import dag, dagEdge, dagVertex

#########################################################    
class dagAdmin(admin.ModelAdmin):
    list_display = ('name',)
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
