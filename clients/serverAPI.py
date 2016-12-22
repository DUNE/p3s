from comms		import data2post, rdec, communicate
from serverURL		import serverURL
########################################################################
class serverAPI(dict):
    def __init__(self, server='http://localhost:8000/', logger=None, verb=0):
        self.server	= server
        self.logger	= logger
        self.verb	= verb
        
        self['job']	= {
            'adjjobURL':	server+'jobs/adj',
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
            'jobReqURL':	server+'pilots/request/?uuid=%s'

        }
        self['workflow']	= {
            'addwfURL':		server+'workflows/addwf',
            'deleteallURL':	server+'workflows/deleteall?what=%s',
            'deleteURL':	server+'workflows/delete',
            'getdagURL':	server+'workflows/getdag?name=%s',
            'adddagURL':	server+'workflows/adddag',
            'addwfURL':		server+'workflows/addwf'

        }

    def setLogger(self, logger):
        self.logger=logger

    def setVerbosity(self, verb):
        self.verb=verb

        
    ############# WORKFLOW
    def registerWorkflow(self, dag, name, description):
        d ={'dag':dag, 'name':name, 'description':description}
        return rdec(communicate(self['workflow']['addwfURL'], data2post(d).utf8()))

    def getDag(self, name):
        return communicate(self['workflow']['getdagURL'] % name)


    def setDag(self, dag):
        return rdec(communicate(self['workflow']['adddagURL'], data2post(dag).utf8()))

    def deleteAllDagWF(self, what):
        return rdec(communicate(self['workflow']['deleteallURL'] % what))


    def deleteDagWF(self, d):
        delData	= data2post(d).utf8()
        return rdec(communicate(self['workflow']['deleteURL'], delData))

    ############# PILOT
    def deleteAllPilots(self):
        return rdec(communicate(self['pilot']['deleteallURL']))

    def deletePilot(self, p_uuid):
        return rdec(communicate(self['pilot']['deleteURL'], data2post(dict(uuid=p_uuid)).utf8()))

    
    def registerPilot(self, p):
        pilotData = data2post(p).utf8()
        if(self.verb>1 and self.logger): self.logger.info('Pilot data in UTF-8: %s' % pilotData)
        return rdec(communicate(self['pilot']['registerURL'], pilotData, self.logger)) # will croak if unsuccessful


    def jobRequest(self, p_uuid):
        return rdec(communicate(self['pilot']['jobReqURL'] % p_uuid))

    def reportPilot(self, p):
        return rdec(communicate(self['pilot']['reportURL'], data2post(p).utf8()))
    
    ############# JOB
    def deleteAllJobs(self):
        return rdec(communicate(self['job']['deleteallURL']))

    def deleteJob(self, d):
        return rdec(communicate(self['job']['deleteURL'], data2post(d).utf8()))

    def addJob(self, j):
        return rdec(communicate(self['job']['addjobURL'], data2post(j).utf8()))
    
    def adjJob(self, j):
        return rdec(communicate(self['job']['adjjobURL'], data2post(j).utf8()))
    ############# DATA
    def registerData(self, d):
        return rdec(communicate(self['data']['registerURL'], data2post(d).utf8(), self.logger))

