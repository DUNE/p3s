# custom imports
import	django_tables2 as tables
from django.utils.safestring		import mark_safe


class Ncolumns(object):
    N = 0
        
    @classmethod
    def setN(cls, N):
        cls.N=N
    @classmethod
    def getN(cls):
        return cls.N

def NavBarData(domain=''):
    links = (
        '<a href="http://'+domain+'/monitor/puritytable">Purity Table</a>',
        '<a href="http://'+domain+'/monitor/puritychart">Purity Charts</a>',
        '<a href="http://'+domain+'/monitor/snchart">S/N Charts</a>',
        '<a href="http://'+domain+'/monitor/runeventdisplay">Event Display by Run and Event</a>',
        '<a href="http://'+domain+'/monitor/eventdisplay">Event Display Image Catalog</a>',
        '<a href="http://'+domain+'/monitor/monrun">Monitor</a>',
        )

    if(domain==''): return len(links)
    
    allLinks = {}
    for n in range(len(links)): allLinks['col'+str(n+1)] = mark_safe(links[n])
    return [allLinks,]
    
class NavTable(tables.Table):
    def __init__(self, *args, **kwargs):
        self.Ncolumns = len(args[0][0].keys())
        super(NavTable, self).__init__(*args,**kwargs)

    for i in range(6): locals()['col'+str(i+1)] = tables.Column()
    
    def set_site(self, site=''):
        self.site=site

        
    class Meta:
        attrs	= {'class': 'paleblue'}


# ---
def TopTable(domain):
    Ncolumns.setN(NavBarData())
    t = NavTable(NavBarData(domain), show_header = False)
    return t

# ---
def HomeBarData(domain, dqm_domain, host=None, port=None):
    # this is for dev only, we want to stay on 8000
    # when we run the dev server
    if port is None: port='8009'
    if(host):
        if('localhost' in host):
            domain = 'localhost:8008'
            dqm_domain = 'localhost:'+port
    if('localhost' in domain):
        domain = 'localhost:8008'
        dqm_domain = 'localhost:'+port
        
    data = []
    data.append({
        'col1':mark_safe('<a href="http://'+domain+'/">p3s Home@'+domain+'</a>'),
        'col2':mark_safe('<a href="http://'+dqm_domain+'/">DQM Home@'+dqm_domain+'</a>'),
    })

    return data

# ---
class AnchorTable(tables.Table):
    col1 = tables.Column()
    col2 = tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}
# ---
def HomeTable(domain, dqm_domain, host=None, port=None):
    t = AnchorTable(HomeBarData(domain, dqm_domain, host, port), show_header = False)
    return t
