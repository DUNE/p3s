from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^wns$',	views.wns,	name='wns'),
]
