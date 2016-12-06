from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^init$',	views.init,	name='init'),
]
