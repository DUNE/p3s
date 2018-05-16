from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^puritytable',views.data_handler2,{'what':'pur','tbl':'PurityTable'},name='puritytable'),
    url(r'^puritychart',views.puritychart,{'what':'purity'},name='puritychart'),
    url(r'^display',views.display,name='EventDisplay'),
]

