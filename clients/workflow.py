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

from comms		import data2post, rdec, communicate
from serverURL		import serverURL
from serverAPI		import serverAPI
#########################################################
def printGraph(g):        
    print("NODES and EDGES representation")
    print("---- NODES ----")
    print(g.nodes())
    for n in g.nodes(): print(n)

    print("---- EDGES ----")
    for e in g.edges(): print(e,g.edge[e[0]][e[1]])

settings.configure(USE_TZ = True)

Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Workflow definitions * 

Option "-g" allows to read and parse contents of a graphML file containing
a workflow description, and send it to the server. A name can be suppplied
via a command line argument, and if absent it is derived from the name of
the file containing the graph.

Workflows are created based on templates which are DAGs which must be
exist on the server.

'''
#-------------------------
class Dag(dict):
    def __init__(self, name='default', description='', graphml=''):
        self['name']		= name
        self['description']	= description
        self['graphml']		= graphml
#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-G", "--get",	action='store_true', help="get a DAG from server - needs the name of the DAG")
parser.add_argument("-H", "--usage",	action='store_true', help="print usage notes and exit")
parser.add_argument("-d", "--delete",	action='store_true', help="deletes a dag or a workflow. Needs name/uuid/type (what).")
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

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage
server	= args.server
verb	= args.verbosity
add	= args.add
delete	= args.delete
what	= args.what
o_uuid	= args.uuid # object uuid
get	= args.get
name	= args.name
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
URLs = serverURL(server=server)
API  = serverAPI(server=server)
######################### DAG DELETE ###################################
# Check if it was a deletion request
if(delete):
    response = None
    if(name=='' and o_uuid==''): exit(-1) # check if we have the key

    # DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(name=='ALL' or o_uuid=='ALL'):
        response = communicate(URLs['workflow']['deleteallURL'] % what)
        if(verb>0): print (rdec(response))
        exit(0)

    # Normal delete (not ALL items)
    delArg = None
    if(name!=''):	delArg = name
    if(o_uuid!=''):	delArg = o_uuid
    
    if ',' in delArg: # assume we have a CSV list
        objList = delArg.split(',')
    else:
        objList.append(delArg)
        

    dicto = None
    for o in objList:
        if(what=='dag'):	dicto = dict(what=what, name=name)
        if(what=='workflow'):	dicto = dict(what=what, uuid=o_uuid)
        delData	= data2post(dicto).utf8()
        response= communicate(URLs['workflow']['deleteURL'], delData) # POST
        if(verb>0): print (rdec(response))

    exit(0)

###################### GET DAG (DIAGNOSTICS) ###########################
if(get):
    if(name==''): exit(-1) # check if we have the key
    resp = API.getDag(name)
    if(verb>0): print (rdec(resp))
    exit(0)
########################## REGISTRATION ################################
# Forms a DAG (workflow template) on the server based on a graph
# description stored in a GraphML file


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
    resp = API.registerWorkflow(add, name, description)
    if(verb>1): print (resp)
    exit(0)

###################### GRAND FINALE ####################################
exit(0)
