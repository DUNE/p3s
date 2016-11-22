from django.contrib import admin

from .models import pilot

class pilotAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'j_uuid', 'site', 'host', 'ts_reg', 'ts_lhb', 'state')
    empty_value_display = '-empty-'
    
admin.site.register(pilot, pilotAdmin)

# Register your models here.
