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
        '<a href="http://'+domain+'/Monitor/PRM">Hardware Purity<br/>Monitor</a>',
        '<a href="http://'+domain+'/monitor/puritytable">Purity<br/>Table</a>',
        '<a href="http://'+domain+'/monitor/puritychart">Purity<br/>Charts</a>',
        '<a href="http://'+domain+'/monitor/monrun?jobtype=purity">Purity<br/>Drift</a>',
        '<a href="http://'+domain+'/monitor/snchart">S/N<br/>Charts</a>',
        '<a href="http://'+domain+'/monitor/monrun?jobtype=monitor">TPC<br/>Monitor</a>',
        '<a href="http://'+domain+'/monitor/monrun?jobtype=femb">FEMB</a>',
        '<a href="http://'+domain+'/monitor/monrun?jobtype=evdisp">2D Raw<br/>Event Display</a>',
#        '<a href="http://'+domain+'/monitor/monrun?jobtype=apa3">APA3</a>',
        '<a href="http://'+domain+'/monitor/monrun?jobtype=reco">Reco</a>',
#        '<a href="http://'+domain+'/monitor/monrun?jobtype=crt">CRT</a>',
#        '<a href="http://'+domain+'/monitor/monrun?jobtype=beam">Beam</a>',
        '<a href="http://'+domain+'/monitor/monrun">All Entries</a>'
        )
    if(domain==''): return len(links)

    allLinks = {}
    for n in range(len(links)):
        allLinks['col'+str(n+1)] = mark_safe(links[n])

    # unfortunately we still need to hadrcode the length of the list later on,
    # tried dynamic but it's crafty anyway -mxp-
    return [allLinks,]

# hardcoded range, ugly but no time to fix
class NavTable(tables.Table):
    def __init__(self, *args, **kwargs):
        self.Ncolumns = len(args[0][0].keys())
        super(NavTable, self).__init__(*args,**kwargs)

    # FIXME - crafty
    for i in range(10): locals()['col'+str(i+1)] = tables.Column()
    
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
        'col1':mark_safe('<a href="https://wiki.dunescience.org/wiki/DQM_Shifter_Manual">Shifter Manual</a>'),
        'col2':mark_safe('<a href="http://'+domain+'/">p3s Home@'+domain+'</a>'),
        'col3':mark_safe('<a href="http://'+dqm_domain+'/">DQM Home@'+dqm_domain+'</a>'),
    })

    return data

# ---
class AnchorTable(tables.Table):
    col1 = tables.Column()
    col2 = tables.Column()
    col3 = tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}
# ---
def HomeTable(domain, dqm_domain, host=None, port=None):
    t = AnchorTable(HomeBarData(domain, dqm_domain, host, port), show_header = False)
    return t

######################### RETIRED LINKS ###############################################
#        '<a href="http://'+domain+'/monitor/runeventdisplay">Event Display by Run and Event</a>',
#        '<a href="http://'+domain+'/monitor/eventdisplay">Event Display Image Catalog</a>',
