from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^puritytable',
	views.data_handler2,
        {'what':'pur','tbl':'PurityTable','url':'puritytable'},
        name='puritytable'),
    
    url(r'^eventdisplay',
	views.data_handler2,
        {'what':'evdisp','tbl':'EvdispTable','url':'eventdisplay'},
        name='evdisptable'),

    url(r'^puritychart',views.puritychart,{'what':'purity'},name='puritychart'),
    
]

