from django.contrib import admin


from .models import service, user

class serviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'ts', 'info')
    empty_value_display = '-empty-'
    
admin.site.register(service, serviceAdmin)

class userAdmin(admin.ModelAdmin):
    list_display = ('name')
    empty_value_display = '-empty-'
    
admin.site.register(user, userAdmin)

