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

    url(r'^monchart',views.monchart,name='monchart'),
    url(r'^puritychart',views.puritychart,{'what':'purity'},name='puritychart'),
    url(r'^snchart',views.puritychart,{'what':'sn'},name='snchart'),

    url(r'^addmon',	views.addmon,  	name='addmon'),
    url(r'^delmon',	views.delmon,  	name='delmon'),
    url(r'^automon',	views.automon, 	name='automon'),
    
    url(r'^display1',	views.display1,	name='display1'),
    url(r'^display6',	views.display6,	name='display6'),

]


# Deprecated. Methods moved to "attic.py"
# url(r'^showmon',	views.showmon,    	name='showmon'),

# url(r'^plot18',
#     views.plot18,
#     name='plot18'),
    
# url(r'^display1',
#     views.display1,
#     name='display1'),



