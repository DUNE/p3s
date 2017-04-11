from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^jobs',	views.data_handler,	{'what':'jobs'},	name='jobs'),
    url(r'^data$',	views.data_handler,	{'what':'data'},	name='data'),
    url(r'^datatypes',	views.data_handler,	{'what':'datatypes'},	name='datatypes'),
    url(r'^pilots',	views.data_handler,	{'what':'pilots'},	name='pilots'),
    url(r'^dags',	views.data_handler,	{'what':'dags'},	name='dags'),
    url(r'^workflows',	views.data_handler,	{'what':'workflows'},	name='workflows'),
    # -----
    url(r'^jobdetail',	views.detail_handler,	{'what':'job'},		name='jobdetail'),
    url(r'^datadetail',	views.detail_handler,	{'what':'dataset'},	name='datadetail'),
    url(r'^pilotdetail',views.detail_handler,	{'what':'pilot'},	name='pilotdetail'),
    url(r'^dagdetail',	views.detail_handler,	{'what':'dag'},		name='dagdetail'),
    url(r'^wfdetail',	views.detail_handler,	{'what':'workflow'},	name='wfdetail'),
]

#    url(r'^dags',	views.dags, 		name='dags'),
#    url(r'^workflows',	views.workflows,	name='workflows'),
