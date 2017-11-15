from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^sites',	views.data_handler,	{'what':'site'},	name='sites'),
    url(r'^jobs',	views.data_handler,	{'what':'job'},		name='jobs'),
    url(r'^data$',	views.data_handler,	{'what':'dataset'},	name='data'),
    url(r'^datatypes',	views.data_handler,	{'what':'datatype'},	name='datatypes'),
    url(r'^pilots',	views.data_handler,	{'what':'pilot'},	name='pilots'),
    url(r'^dags',	views.data_handler,	{'what':'dag'},		name='dags'),
    url(r'^workflows',	views.data_handler,	{'what':'workflow'},	name='workflows'),
    url(r'^services',	views.data_handler,	{'what':'service'},	name='services'),
    # -----
    url(r'^sitedetail',	views.detail_handler,	{'what':'site'},	name='sitedetail'),
    url(r'^jobdetail',	views.detail_handler,	{'what':'job'},		name='jobdetail'),
    url(r'^datadetail',	views.detail_handler,	{'what':'dataset'},	name='datadetail'),
    url(r'^pilotdetail',views.detail_handler,	{'what':'pilot'},	name='pilotdetail'),
    url(r'^dagdetail',	views.detail_handler,	{'what':'dag'},		name='dagdetail'),
    url(r'^wfdetail',	views.detail_handler,	{'what':'workflow'},	name='wfdetail'),
    # -----
    url(r'^filesystem',	views.filesystem,	name='filesystem'),
]

#    url(r'^dags',	views.dags, 		name='dags'),
#    url(r'^workflows',	views.workflows,	name='workflows'),
