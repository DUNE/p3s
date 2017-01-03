#!/usr/bin/env python3
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
import json
from pprint		import pprint

import networkx as nx

from serverAPI		import serverAPI
#########################################################
# simple printout for visual verification of a DAG
def printGraph(g):        
    print("NODES and EDGES representation of the DAG")
    print("---- NODES ----")
    print(g.nodes())
    for n in g.nodes(): print(n)
    print("---- EDGES ----")
    for e in g.edges(): print(e,g.edge[e[0]][e[1]])
# ---
settings.configure(USE_TZ = True)

Usage		= '''Usage:
For command line options run the script with "--help" option.
* Terminology *
DAG is an abstraction of a workflow i.e. it describes its topology
and general characteristics of edges and vertices but does not
correspond to a running process nor does it have a complete information
to create a functional workflow. Workflows are created based on DAGs
serving as templates.

* DAG definition * 
Option "-g" allows to use a graphML file containing a DAG description
and send it to the server. A name can be suppplied via a command line
argument, and if absent it is derived from the name of the file containing
the graph.

DAG names are unique which is enforced in the database.

* Workflow definitions * 

Workflows are created based on templates (DAGs) which must be
exist on the server by the time a request for a new workflow is sent.
A name can be optionally set for a workflow but it's not expected
to be unique. Worflows are idnetified in the system by their UUIDs which
are automatically generated.

* Deletion *

Until serious testing has been completed, please leave this
operation to the experts, such as the author of this software.

'''
#-------------------------
class Dag(dict):
    def __init__(self, name='default', description='', graphml=''):
        self['name']		= name
        self['description']	= description
        self['graphml']		= graphml
#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-G", "--get",	help="get a DAG from server - needs the name of the DAG",	action='store_true')
parser.add_argument("-U", "--usage",	help="print usage notes and exit",				action='store_true')
parser.add_argument("-d", "--delete",	help="deletes a dag or workflow. Needs name/uuid+type (what)",	action='store_true')

parser.add_argument("-m", "--modify",	help='''modifies the state of a workflow, needs uuid and the desired new state (except "template")''',
                    action='store_true')

parser.add_argument("-D", "--description",type=str,	default='', help="Description (optional).")
parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/', help="the server, default: http://localhost:8000/")
parser.add_argument("-w", "--what",	type=str,	default='', help="dag or workflow (for deletion).")
parser.add_argument("-v", "--verbosity",type=int,	default=0, choices=[0, 1, 2], help="set verbosity - also needed for data output.")
parser.add_argument("-u", "--uuid",	type=str,	default='', help="uuid of the objet to be modified or deleted")
parser.add_argument("-g", "--graphml",	type=str,	default='', help="Create a DAG on the server from a GraphML file.")
parser.add_argument("-n", "--name",	type=str,	default='', help="The name of the DAG or workflow to be manipulated.")
parser.add_argument("-a", "--add",	type=str,	default='',
                    help='''Add a workflow. Argument is the name of the prototype DAG (already stored on the server).
                    If no special name is provided for the workflow via the *name* argument,
                    defaults to the name of the parent DAG''')

parser.add_argument("-f", "--fileinfo",	type=str,	default='',
                    help='''Provides file information for the workflow, overriding filenames
                    and directory paths in the DAG template. Can be a name of a JSON file if the string
                    contains ".json", otherwise the string itself provides the info, formatted as a JSON
                    dictionary with the pattern {'source:target':{"name":"foo","dirpath":"bar"}}. Can
                    also include "comment":"my new comment" in the dictionary.''')

parser.add_argument("-j", "--jobinfo",	type=str,	default='',
                    help='''Provides job information for the workflow, similar to "fileinfo"''')

parser.add_argument("-s", "--state",	type=str,	default='template', help='''set/modify the state of a workflow.
Needs uuid to modify or can be used at creation time.''')

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage
server	= args.server
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

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
objList = []

###################### USAGE PRINT AND EXIT ############################
if(usage):
    print(Usage)
    exit(0)
########################################################################
API  = serverAPI(server=server)
######################### DAG DELETE ###################################
# Check if it was a deletion request
if(delete):
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
        if(what=='workflow'):	dicto = dict(what=what, uuid=o)
        resp = API.deleteDagWF(dicto)
        if(verb>0): print(resp)

    exit(0)

###################### GET DAG (DIAGNOSTICS) ###########################
if(get):
    if(name==''): exit(-1) # check if we have the key
    resp = API.getDag(name)
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
    resp = API.setDag(d)

    if(verb>1): print (resp)

    exit(0)

########################################################################
if(add!=''):
    if(name==''): name=add

    f = None
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
    
    resp = API.registerWorkflow(add, name, state, fileinfo, jobinfo, description)
    
    if(verb>1): print (resp)
    exit(0)

########################################################################
if(modify):
    if(state=='template'): exit(0) # won't modify what's already a default
    if(o_uuid==''): exit(-1) # can't proceed without a key
    resp = API.setWorkflowState(o_uuid, state)
    
    if(verb>1): print (resp)
    exit(0)
    

###################### GRAND FINALE ####################################
exit(0)
