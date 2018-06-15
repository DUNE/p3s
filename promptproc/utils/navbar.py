# custom imports
import	django_tables2 as tables
from django.utils.safestring		import mark_safe


def NavBarData(domain, dqm_domain):
    data = []
    data.append({
        'col1':mark_safe('<a href="http://'+domain+'/monitor/jobs">Jobs</a>'),
        'col2':mark_safe('<a href="http://'+domain+'/monitor/pilots">Pilots</a>'),
        'col3':mark_safe('<a href="http://'+domain+'/monitor/workflows">Workflows</a>'),
        'col4':mark_safe('<a href="http://'+domain+'/monitor/dags">DAGs</a>'),
        'col5':mark_safe('<a href="http://'+domain+'/monitor/data">Data</a>'),
        'col6':mark_safe('<a href="http://'+domain+'/monitor/datatypes">Data Types</a>'),
        'col7':mark_safe('<a href="http://'+domain+'/monitor/services">Services</a>'),
        'col8':mark_safe('<a href="http://'+domain+'/monitor/sites">Sites</a>'),
        'col9':mark_safe('<a href="http://'+domain+'/">p3s Home@'+domain+'</a>'),
        'col10':mark_safe('<a href="http://'+domain+'/">DQM Home@'+dqm_domain+'</a>'),
    })

    return data
    
class NavTable(tables.Table):
    col1 = tables.Column()
    col2 = tables.Column()
    col3 = tables.Column()
    col4 = tables.Column()
    col5 = tables.Column()
    col6 = tables.Column()
    col7 = tables.Column()
    col8 = tables.Column()
    col9 = tables.Column()
    col10 = tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}


def TopTable(domain, dqm_domain):
    t = NavTable(NavBarData(domain, dqm_domain), show_header = False)
    return t
