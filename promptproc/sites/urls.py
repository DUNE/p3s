from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^wns$',	views.wns,	name='wns'),
    url(r'^define$',	views.define,	name='define'),
    url(r'^delete$',	views.delete,	name='delete'),
    url(r'^$',		views.sites,	name='sites'),
]
