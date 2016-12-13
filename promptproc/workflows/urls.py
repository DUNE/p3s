from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^init$',	views.init,	name='init'),
    url(r'^adddag$',	views.adddag,	name='adddag'),
    url(r'^getdag$',	views.getdag,	name='getdag'),
    url(r'^delete$',	views.delete,	name='delete'),
]
