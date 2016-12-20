from comms		import data2post, rdec, communicate
from serverURL		import serverURL
########################################################################
class serverAPI(dict):
    def __init__(self, server='http://localhost:8000/'):
        self.server	= server
        self['job']	= {
            'jobsetURL':	server+'jobs/set',
            'deleteallURL':	server+'jobs/deleteall',
            'deleteURL':	server+'jobs/delete',
            'addjobURL':	server+'jobs/addjob'

        }
        self['data']	= {
            'registerURL':	server+'data/register',

        }
        self['pilot']	= {
            'reportURL':	server+'pilots/report',
            'registerURL':	server+'pilots/register',
            'deleteURL':	server+'pilots/delete',
            'deleteallURL':	server+'pilots/deleteall',
            'jobReqURL':	server+'pilots/request/?uuid=%s'}
        self['workflow']	= {
            'addwfURL':		server+'workflows/addwf',
            'deleteallURL':	server+'workflows/deleteall?what=%s',
            'deleteURL':	server+'workflows/delete',
            'getdagURL':	server+'workflows/getdag?name=%s',
            'adddagURL':	server+'workflows/adddag',
            'addwfURL':		server+'workflows/addwf'

        }
        
    def registerWorkflow(self, dag, name, description):
        d ={'dag':dag, 'name':name, 'description':description}

        wfData	= data2post(d).utf8()
        return rdec(communicate(self['workflow']['addwfURL'], wfData))

    def getDag(self, name):
        return communicate(self['workflow']['getdagURL'] % name)


    def setDag(self, dag):
        return rdec(communicate(self['workflow']['adddagURL'], data2post(dag).utf8()))
