from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^registerdata',	views.registerdata,	name='registerdata'),
    url(r'^registertype',	views.registertype,	name='registertype'),
    url(r'^deletedatatype',	views.deletedatatype,	name='deletedatatype'),
    url(r'^deletedata',		views.deletedata,	name='deletedata'),
    url(r'^adjustdata',		views.adjustdata,	name='adjustdata'),
]
