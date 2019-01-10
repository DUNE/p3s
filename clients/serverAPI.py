###########################################################################
# This is a dictionary which maps mneumonic keys to URLs of the p3s       #
# server. It thus allows for more flexibility when changing URLs and also #
# serves as a reference to the server API.                                #
###########################################################################

from comms		import data2post, rdec, communicate


###########################################################################
class serverAPI(dict):
    def __init__(self, server='http://localhost:8000/', logger=None, verb=0):
        
        self.server	= server
        self.logger	= logger
        self.verb	= verb

        ### INFO
        self['info']	= {
            'dash':	server+'%s',
            'pilotinfo':server+'pilotinfo'+'%s',
        }

        ### JOB
        self['job']	= {
            'adjust':	server+'jobs/adjust',
            'delete':	server+'jobs/delete',
            'purge':	server+'jobs/purge',
            'add':	server+'jobs/add',
            'ltype':	server+'jobs/ltype?name=%s',
            'limit':	server+'jobs/limit',
        }

        ### SITE
        self['site']	= {
            'getsiteURL':server+'sites?name=%s',
            'defineURL': server+'sites/define',
            'deleteURL': server+'sites/delete',
        }

        ### DATA
        self['data']	= {
            'register':		server+'data/register',
            'delete':		server+'data/delete',
            'adjust':		server+'data/adjust',
            'registertype':	server+'data/registertype',
            'deletetype':	server+'data/deletetype',
            'getdata':		server+'data/getdata?name=%s',
        }

        ### PILOT
        self['pilot']	= {
            'reportURL':	server+'pilots/report',
            'registerURL':	server+'pilots/register',
            'delete':		server+'pilots/delete',
            'kill':		server+'pilots/kill',
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

        ### LOGIC
        self['logic']	= {
            'purge':	server+'logic/purge',
            'pilotTO':	server+'logic/pilotTO',
            'jobTO':	server+'logic/jobTO',
            'service':	server+'logic/service',
            'delete':	server+'logic/delete',
        }

        ### DQM purity
        self['purity']	= {
            'add':	server+'purity/add',
            'delete':	server+'purity/delete',
            'index':	server+'purity/index/%s',
        }

        ### DQM evdisp
        self['evd']	= {
            'add':	server+'evd/add',
            'delete':	server+'evd/delete',
            'maxrun':	server+'evd/maxrun/%s',
        }

        ### DQM monitor
        self['monitor']	= {
            'addmon':	server+'monitor/addmon',
            'delmon':	server+'monitor/delmon',
            'move':	server+'monitor/move',
        }


    def setLogger(self, logger):
        self.logger=logger

    def setVerbosity(self, verb):
        self.verb=verb

        
    ############# GENERAL POST & GET
    def post2server(self, view, url, stuff):
        # print('************', view, url, stuff, self[view][url])
        return rdec(communicate(self[view][url], data=data2post(stuff).utf8(), logger=self.logger, verb=self.verb))
    
    def get2server(self, view, url, stuff):
        if(self.verb>0): print(self[view][url] % stuff)
        resp = communicate(self[view][url] % stuff, logger=self.logger)
        return rdec(resp)


    
    #############
    # Some wrappers for convenience, will keep for now
    
    ############# WORKFLOW
    def deleteAllDagWF(self, what):
        return rdec(communicate(self['workflow']['deleteallURL'] % what, logger=self.logger))

    ############# PILOT
    def registerPilot(self, p):
        pilotData = data2post(p).utf8()
        if(self.verb>1 and self.logger): self.logger.info('Pilot data in UTF-8: %s' % pilotData)
        return rdec(communicate(self['pilot']['registerURL'], pilotData, self.logger)) # will croak if unsuccessful

    def reportPilot(self, p):
        return self.post2server('pilot', 'reportURL', p)

    ############# DATA /deprecated
    #    def registerData(self, d):
    #        return rdec(communicate(self['data']['register'], data2post(d).utf8(), self.logger))

    #    def adjData(self, d):
    #        return rdec(communicate(self['data']['adjdata'], data2post(d).utf8()))

