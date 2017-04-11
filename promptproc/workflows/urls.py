from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^init$',	views.init,	name='init'),
    url(r'^adddag$',	views.adddag,	name='adddag'),
    url(r'^getdag$',	views.getdag,	name='getdag'),
    url(r'^addwf$',	views.addwf,	name='addwf'),
    url(r'^setwfstate$',views.setwfstate,name='setwfstate'),
    url(r'^delete$',	views.delete,	name='delete'),
    url(r'^deleteall$',	views.deleteall,name='deleteall'),
]
