from django.contrib import admin
from .models import site

############
class siteAdmin(admin.ModelAdmin):
    list_display = ('name', 'env', 'server', 'pilotcycles', 'pilotperiod',)
    empty_value_display = '-empty-'
    
admin.site.register(site, siteAdmin)
