from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^pilots',	views.pilots,	name='pilots'),
    url(r'^jobs',	views.jobs,	name='jobs'),
]
