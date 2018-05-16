from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^addpurity',	views.addpurity,	name='addpurity'),
    url(r'^delpurity',	views.delpurity,	name='delpurity'),
    url(r'^indpurity',	views.indpurity, 	name='indpurity'),
]

