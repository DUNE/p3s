# custom imports
import	django_tables2 as tables
from django.utils.safestring		import mark_safe


def NavBarData(domain):
    data = []
    purityTableLink	= mark_safe('<a href="http://'+domain+'/monitor/puritytable">Purity Table</a>')
    purityChartLink	= mark_safe('<a href="http://'+domain+'/monitor/purityshart">Purity Charts</a>')
    evdispRunLink	= mark_safe('<a href="http://'+domain+'/monitor/runeventdisplay">Event Display by Run and Event</a>')
    evdispCatalogLink	= mark_safe('<a href="http://'+domain+'/monitor/eventdisplay">Event Display Image Catalog</a>')
    
    data.append({
        'col1':purityTableLink,
        'col2':purityChartLink,
        'col3':evdispRunLink,
        'col4':evdispCatalogLink,
    })

    return data
    
class NavTable(tables.Table):
    col1	= tables.Column()
    col2	= tables.Column()
    col3	= tables.Column()
    col4	= tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}


def TopTable(domain):
    t = NavTable(NavBarData(domain), show_header = False)
    return t
