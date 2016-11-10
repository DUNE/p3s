from django.contrib import admin

from .models import pilot

class pilotAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'state', 'ts_created', 'ts_reg')
    empty_value_display = '-empty-'
    
admin.site.register(pilot, pilotAdmin)

# Register your models here.
