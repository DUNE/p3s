from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^puritytable',
	views.data_handler2,
        {'what':'pur','tbl':'PurityTable','tblHeader':'Purity Table','url':'puritytable'},
        name='puritytable'),
    
    url(r'^eventdisplay',
	views.data_handler2,
        {'what':'evdisp','tbl':'EvdispTable','tblHeader':'Image Catalog','url':'eventdisplay'},
        name='evdisptable'),

    url(r'^runeventdisplay',
	views.data_handler2,
        {'what':'evdisp','tbl':'RunTable','tblHeader':'Available Runs','url':'runeventdisplay'},
        name='evdisptable'),

    url(r'^monrun',
	views.data_handler2,
        {'what':'monrun','tbl':'MonRunTable','tblHeader':'Monitor Runs','url':'monrun'},
        name='monruntable'),

    url(r'^puritychart',views.puritychart,{'what':'purity'},name='puritychart'),
    
    url(r'^display1',
	views.display1,
        name='display1'),

    url(r'^display6',
	views.display6,
        name='display6'),

    url(r'^plot16',
	views.plot16,
        name='plot16'),


    url(r'^addmon',	views.addmon,    	name='addmon'),

]

