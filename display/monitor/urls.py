from django.conf.urls import url

from . import views
import purity.views as purityViews
import evdisp.views as evdispViews

urlpatterns = [
    url(r'^puritytable',views.data_handler2,	{'what':'purity'},	name='puritytable'),
    url(r'^puritychart',views.puritychart,	{'what':'purity'},	name='puritychart'),
    url(r'^display',	views.display,	      	name='evdisp'),
    url(r'^test',	evdispViews.test,    	name='evdisp'),
    url(r'^addpurity',	purityViews.addpurity,	name='addpurity'),
    url(r'^delpurity',	purityViews.delpurity,	name='delpurity'),
    url(r'^indpurity',	purityViews.indpurity, 	name='indpurity'),
]

