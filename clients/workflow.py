#!/usr/bin/env python3.5
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################
# Please disregard bits of code "left for later" - most #
# will be used for future development                   #
#########################################################

from django.conf	import settings
from django.utils	import timezone

import argparse
import uuid
import socket
import time
import datetime
import logging
import json
import os

import networkx as nx

from serverAPI import serverAPI
from clientenv import clientenv

#########################################################
# simple printout for visual verification of a DAG on the client side
def printGraph(g):        
    print("NODES and EDGES representation of the DAG")
    print("---- NODES ----")
    print(g.nodes())
    for n in g.nodes(): print(n)
    print("---- EDGES ----")
    for e in g.edges(): print(e,g.edge[e[0]][e[1]])
# ---
settings.configure(USE_TZ = True)

#-------------------------
class Dag(dict):
    def __init__(self, name='default', description='', graphml=''):
        self['name']		= name
        self['user']		= user
        self['description']	= description
        self['graphml']		= graphml

    def __str__(self):
        myStr=''
        for k in self.keys():
#            if(k=='graphml'): continue
            myStr+=k+':'+self[k]+'\n'
        return myStr


#-------------------------
envDict = clientenv(outputDict=True)

user = envDict['user']

logdefault	= '/tmp/'+user+'/p3s/workflows'
host		= socket.gethostname()

parser = argparse.ArgumentParser()

parser.add_argument("-l", "--logdir",	type=str,	default=logdefault,
                    help="(defaults to "+logdefault+") the path for the logs")

parser.add_argument("-G", "--get",	help="the name of a DAG to download from server", type=str, default='')

parser.add_argument("-U", "--usage",	help="print usage notes and exit",				action='store_true')

parser.add_argument("-d", "--delete",	help="deletes a dag or workflow. Needs name/uuid+type (what)",	action='store_true')

parser.add_argument("-m", "--modify",	help="modifies the state of a workflow, needs uuid/new state",	action='store_true')

parser.add_argument("-D", "--description",type=str,	default='', help="Description (optional).")

parser.add_argument("-S", "--server",	type=str,	default=envDict['server'],
                    help="the server address, defaults to $P3S_SERVER or if unset to http://localhost:8000/")

parser.add_argument("-w", "--what",	type=str,	default='',choices=['workflow','dag'],
                    help="type of object(s) for deletion")

parser.add_argument("-v", "--verbosity", type=int,	default=envDict['verb'], choices=[0, 1, 2, 3, 4],
                    help="output verbosity (0-4), will default to $P3S_VERBOSITY if set")

parser.add_argument("-u", "--uuid",	type=str,	default='', help="uuid of the objet to be modified or deleted")

parser.add_argument("-g", "--graphml",	type=str,	default='', help="Create a DAG on the server from a GraphML file.")

parser.add_argument("-n", "--name",	type=str,	default='', help="The name of the DAG or workflow to be manipulated.")

parser.add_argument("-a", "--add",	type=str,	default='',
                    help='''Add a workflow. Argument is the name of the prototype DAG (already stored on the server).
                    If no special name is provided for the workflow via the *name* argument,
                    defaults to the name of the parent DAG''')

parser.add_argument("-f", "--fileinfo",	type=str,	default='',
                    help='''Provides file information for the workflow, overriding filenames
                    and directory paths in the DAG template. Can be a special string (see usage notes),
                    a name of a JSON file if the string contains ".json", otherwise the string will be assumed
                    formatted as a JSON dictionary with the pattern {'source:target':{"name":"foo","dirpath":"bar"}}. Can
                    also include "comment":"my new comment" in the dictionary.''')

parser.add_argument("-j", "--jobinfo",	type=str,	default='',
                    help='''Provides job information for the workflow, similar to "fileinfo"''')

parser.add_argument("-s", "--state",	type=str,	default='template', help='''set/modify the state of a workflow.
Needs uuid to modify or can be used at creation time.''')

parser.add_argument("-t", "--test",	action='store_true',	help="when set, do not contact the server")

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage
server	= args.server
logdir	= args.logdir
verb	= args.verbosity
add	= args.add
delete	= args.delete
modify	= args.modify
what	= args.what
o_uuid	= args.uuid # object uuid
get	= args.get
name	= args.name
state	= args.state
fileinfo= args.fileinfo
jobinfo	= args.jobinfo
graphml	= args.graphml
description = args.description
tst	= args.test

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
objList = []

###################### USAGE PRINT AND EXIT ############################
if(usage):
    try:
        f = open('WORKFLOW.md','r')
        s = f.read()
        print(s)
    except:
        print('Local text file not found, please consult the WORKFLOW document in the documents directory')
        exit(-1)

    exit(0)
###################### PREPARE LOG DIRECTORY AND FILE ##################
if(not os.path.exists(logdir)):
    try:
        os.makedirs(logdir)
    except:
        exit(-1) # we can't log it

        
logfilename = logdir+'/workflow.log'


logger = logging.getLogger('p3sworkflow')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
logger.info('START on host %s, user %s, p3s server %s, verbosity %s' %
            (host, user, server, verb))

########################################################################
API  = serverAPI(server=server, logger=logger)


########################################################################
######################### DAG DELETE ###################################
# Check if it was a deletion request
if(delete):
    if(what==''):
        print('Type of object for deletion not specified, exiting...')
        exit(-2)
    if(name=='' and o_uuid==''): exit(-1) # check if we have the key

    # DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(name=='ALL' or o_uuid=='ALL'):
        resp = API.deleteAllDagWF(what)
        if(verb>0): print(resp)
        exit(0)

    # Normal delete (not ALL items)
    delArg = None
    if(name!=''):	delArg = name
    if(o_uuid!=''):	delArg = o_uuid
    
    if ',' in delArg: # assume we have a CSV list
        objList = delArg.split(',')
    else:
        objList.append(delArg)
        
    for o in objList:
        dicto = None
        if(what=='dag'):	dicto = dict(what=what, name=o)
        if(what=='workflow' and o_uuid!=''):	dicto = dict(what=what, uuid=o)
        if(what=='workflow' and name!=''):	dicto = dict(what=what, name=o)
        resp = API.post2server('workflow', 'deleteURL', dicto)
        if(verb>0): print(resp)

    exit(0)

###################### GET DAG (DIAGNOSTICS) ###########################
if(get!=''):
    if(verb>0): print('Attempting to fetch DAG "'+get+'" from the server')
    resp = API.get2server('workflow','getdagURL', get)
    if(verb>0): print(resp)
    exit(0)

########################## REGISTRATION ################################
# Forms a DAG (workflow template) on the server based on a graph
# description stored in a GraphML file. Note that the content is
# verified by NetworkX first, then a string in GraphML format is
# forwarded to the server.
if(graphml!=''):
    if(name==''): # default to the root of the file name
        basename = graphml.rsplit( ".", 1 )[0] # admittedly crafty
        segs = basename.rsplit("/",1)
        name = segs[-1]
    
    if(verb>1): print ('Request for DAG "%s". Reading file %s' % (name, graphml))
    g = nx.read_graphml(graphml)
    if(verb>0): printGraph(g)

    s = '\n'.join(nx.generate_graphml(g))

    d = Dag(name=name, description=description, graphml=s)
    if(verb>1): print('DAG:\n----------------------\n', d,'\n-------------\n')
    if(tst): exit(0)
    
    resp = API.post2server('workflow', 'adddagURL', d)

    if(verb>1): print (resp)

    exit(0)

########################################################################
if(add!=''):
    if(name==''): name=add

    f = None # just a placeholder for a file handle used later

    # Now, if strings contain "json" these will be assumed to be filenames
    # and if not, the strings will be passed through to the server
    
    if('.json' in fileinfo):
        try:
            f = open(fileinfo, 'r')
            content = f.read()
            f.close()
            if(verb>1): print(content)
            fileinfo = content
        except:
            print('Problems reading input file %s' % fileinfo)
            exit(-1)
            
    if('.json' in jobinfo):
        try:
            f = open(jobinfo, 'r')
            content = f.read()
            f.close()
            if(verb>1): print(content)
            jobinfo = content
        except:
            print('Problems reading input file %s' % jobinfo)
            exit(-1)

    # note that "fileinfo" and "jobinfo" default to an empty string when we parse
    # arguments, and will be passed to the server even if they are indeed empty
    wf = {
        'dag':		add,
        'user':		user,
        'name':		name,
        'state':	state,
        'fileinfo':	fileinfo,
        'jobinfo':	jobinfo,
        'description':	description
    }

    resp = API.post2server('workflow', 'addwfURL', wf)
    
    if(verb>1): print (resp)
    exit(0)

########################################################################
if(modify):
    if(state=='template'): exit(0) # won't modify what's already a default
    if(o_uuid==''): exit(-1) # can't proceed without a key

    d = {'uuid': o_uuid, 'state': state}

    resp = API.post2server('workflow', 'setwfstateURL', d)
    
    if(verb>1): print (resp)
    exit(0)
    

###################### GRAND FINALE ####################################
exit(0)
