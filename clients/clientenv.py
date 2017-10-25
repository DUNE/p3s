#!/usr/bin/env python3.5
import os
#########################################################
def clientenv(outputDict=False):

    (user, server, dqmserver,
     verb, site, dirpath) = ('', 'http://localhost:8000/','http://localhost:8000/',
                             0, 'default', 'dummypath')

    
    
    # dummy path will fail if not set later to a valid value - on purpose
    # dqmserver = "http://serenity.local:8000/"
    
    e = os.environ.keys()
    
    if 'USER' in e:
        user = os.environ['USER']
    else:
        print('EXITING: could not determine the user')
        exit(7)

    pilotlog	= '/tmp/'+user+'/p3s/pilots'
    joblog	= '/tmp/'+user+'/p3s/jobs'

        
    if 'P3S_SERVER'	in e:	server	= os.environ['P3S_SERVER']
    if 'P3S_VERBOSITY'	in e:	verb	= os.environ['P3S_VERBOSITY']
    if 'P3S_SITE'	in e:	site	= os.environ['P3S_SITE']

    if 'P3S_PILOTLOG'	in e:	pilotlog= os.environ['P3S_PILOTLOG']
    if 'P3S_JOBLOG'	in e:	joblog	= os.environ['P3S_JOBLOG']

    if 'P3S_DIRPATH'	in e:	dirpath	= os.environ['P3S_DIRPATH']
    if 'DQM_SERVER'	in e:	dqmserver= os.environ['DQM_SERVER']

    
    if(outputDict):
        d = {}
        d['user']	= user
        d['server']	= server
        d['dqmserver']	= dqmserver
        d['verb']	= verb
        d['site']	= site
        d['pilotlog']	= pilotlog
        d['joblog']	= joblog
        d['dirpath']	= dirpath

        return d

    else:
        return (user, server, verb, site, pilotlog, joblog)

