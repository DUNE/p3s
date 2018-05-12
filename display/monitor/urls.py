from django.conf.urls import url

from . import views
import purity.views as purityViews

urlpatterns = [
    url(r'^puritytable',views.data_handler2,	{'what':'purity'},	name='puritytable'),
    url(r'^puritychart',views.puritychart,	{'what':'purity'},	name='puritychart'),
    url(r'^evdisp',	views.evdisp,	      	name='evdisp'),
    url(r'^addpurity',	purityViews.addpurity,	name='addpurity'),
    url(r'^delpurity',	purityViews.delpurity,	name='delpurity'),
    url(r'^indpurity',	purityViews.indpurity, 	name='indpurity'),
]

