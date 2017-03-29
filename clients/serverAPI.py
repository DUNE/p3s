from comms		import data2post, rdec, communicate
########################################################################
class serverAPI(dict):
    def __init__(self, server='http://localhost:8000/', logger=None, verb=0):
        self.server	= server
        self.logger	= logger
        self.verb	= verb

        ### JOB
        self['job']	= {
            'adjust':	server+'jobs/adjust',
            'delete':	server+'jobs/delete',
            'add':	server+'jobs/add',
        }

        ### DATA
        self['data']	= {
            'registerdataURL':	server+'data/registerdata',
            'registertypeURL':	server+'data/registertype',
            'deletetypeURL':	server+'data/deletetype',
            'adjdataURL':	server+'data/adjustdata',
        }

        ### PILOT
        self['pilot']	= {
            'reportURL':	server+'pilots/report',
            'registerURL':	server+'pilots/register',
            'delete':		server+'pilots/delete',
            'jobRequestURL':	server+'pilots/request',
        }

        ### WORKFLOW
        self['workflow']	= {
            'addwfURL':		server+'workflows/addwf',
            'setwfstateURL':	server+'workflows/setwfstate',
            'deleteallURL':	server+'workflows/deleteall?what=%s',
            'deleteURL':	server+'workflows/delete',
            'getdagURL':	server+'workflows/getdag?name=%s',
            'adddagURL':	server+'workflows/adddag',
            'addwfURL':		server+'workflows/addwf',
        }


    def setLogger(self, logger):
        self.logger=logger

    def setVerbosity(self, verb):
        self.verb=verb

        
    ############# GENERAL POST & GET
    def post2server(self, view, url, stuff):
        return rdec(communicate(self[view][url], data2post(stuff).utf8(), self.logger))
    
    def get2server(self, view, url, stuff):
        return rdec(communicate(self[view][url] % stuff))
    
    ############# WORKFLOW
    def deleteAllDagWF(self, what):
        return rdec(communicate(self['workflow']['deleteallURL'] % what))

    ############# PILOT
    def registerPilot(self, p):
        pilotData = data2post(p).utf8()
        if(self.verb>1 and self.logger): self.logger.info('Pilot data in UTF-8: %s' % pilotData)
        return rdec(communicate(self['pilot']['registerURL'], pilotData, self.logger)) # will croak if unsuccessful

    def reportPilot(self, p):
        return self.post2server('pilot', 'reportURL', p)

    # return rdec(communicate(self['pilot']['reportURL'], data2post(p).utf8()))
    
    ############# DATA
    def registerData(self, d):
        return rdec(communicate(self['data']['registerdataURL'], data2post(d).utf8(), self.logger))

    def registerType(self, d):
        return rdec(communicate(self['data']['registertypeURL'], data2post(d).utf8(), self.logger))

    def deleteType(self, d):
        return rdec(communicate(self['data']['deletetypeURL'], data2post(d).utf8(), self.logger))

    def adjData(self, d):
        return rdec(communicate(self['data']['adjdataURL'], data2post(d).utf8()))

