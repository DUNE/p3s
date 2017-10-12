from django.conf.urls import url

from . import views
import purity.views as purityViews



urlpatterns = [
    url(r'^purity',	views.data_handler,	{'what':'purity'},	name='purity'),
    url(r'^addpurity',	purityViews.addpurity,	name='addpurity'),
    url(r'^delpurity',	purityViews.delpurity,	name='delpurity'),
    url(r'^indpurity',	purityViews.indpurity, 	name='indpurity'),
]
