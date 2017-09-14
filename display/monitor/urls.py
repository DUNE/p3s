from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^purity',	views.data_handler,	{'what':'purity'},	name='purity'),
]
