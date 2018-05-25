from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^test',	views.test,    	name='yesy'),
    url(r'^add',	views.add,    	name='add'),
    url(r'^delete',	views.delete,  	name='delete'),
    url(r'^maxrun',	views.maxrun,  	name='maxrun'),
]

