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

import urllib
from urllib		import request
from urllib		import error
from urllib.error	import URLError

import networkx as nx
import io

# local import, may require PYTHONPATH to be set
from comms		import data2post, rdec, communicate


#########################################################
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

        # self['uuid']	= uuid.uuid1()
        # self['stage']	= stage
        # self['priority']= priority
        # self['state']	= state
        # self['subhost']	= socket.gethostname() # submission host
        # self['ts']	= str(timezone.now()) # see TZ note on top

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-g", "--graphml",	type=str,	default='',
                    help="Create a DAG on the server, using a GraphML file as input.")

parser.add_argument("-n", "--name",	type=str,	default='',
                    help="The name of the DAG or workflow to be manipulated, depending on the context.")

parser.add_argument("-a", "--add",	type=str,	default='',
                    help='''Add a workflow. Argument is the name of the prototype DAG (stored on the server).
                    If no special name is provided for the workflow via the *name* argument,
                    defaults to the name of the parent DAG''')

parser.add_argument("-D", "--description",	type=str,	default='',
                    help="Description of the DAG or workflow (optional).")

parser.add_argument("-o", "--out",	action='store_true',
                    help="output the graph to stdout")

parser.add_argument("-G", "--get",	action='store_true',
                    help="get a DAG from server - needs the name of the DAG")


parser.add_argument("-H", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a dag or a workflow. Needs a name or uuid, and the type (what).")

parser.add_argument("-w", "--what",	type=str,	default='',
                    help="dag or workflow (for deletion).")

parser.add_argument("-v", "--verbosity",	type=int, default=0, choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-u", "--uuid",	type=str,	default='',
                    help="uuid of the objet to be modified or deleted")

########################## Left for later (maybe) ######################
# parser.add_argument("-s", "--state",	type=str,	default='',
#                    help="sets the job state, needs *adjust* option to be activated")
#parser.add_argument("-p", "--priority",	type=int,	default=-1,
#                    help="sets the job priority, needs *adjust* option to be activated")
#parser.add_argument("-i", "--id",	type=str,	default='',
#                    help="id of the job to be adjusted (pk)")
#parser.add_argument("-t", "--test",	action='store_true',
#                    help="when set, forms a request but does not contact the server")

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
out	= args.out

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
objList = []

deleteallURL	= server+'workflows/deleteall?what=%s'
deleteURL	= server+'workflows/delete'
getdagURL	= server+'workflows/getdag?name=%s'
adddagURL	= server+'workflows/adddag'
addwfURL	= server+'workflows/addwf'
###################### USAGE PRINT AND EXIT ############################
if(usage):
    print(Usage)
    exit(0)

######################### DAG DELETE ###################################
# Check if it was a deletion request
if(delete):
    response = None
    if(name=='' and o_uuid==''): exit(-1) # check if we have the key

    # DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(name=='ALL' or o_uuid=='ALL'):
        response = communicate(deleteallURL % what)
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
        response= communicate(deletlURL, delData) # POST
        if(verb>0): print (rdec(response))

    exit(0)

###################### GET DAG (DIAGNOSTICS) ###########################
if(get):
    response = None
    if(name==''): exit(-1) # check if we have the key
    response = communicate(getdagURL % name)
    if(verb>0): print (rdec(response))
    exit(0)
########################## REGISTRATION ################################
# Forms a DAG (workflow template) on the server based on a graph
# description stored in a GraphML file


if(graphml!=''):
    if(name==''): # default to the root of the file name
        basename = graphml.rsplit( ".", 1 )[0]
        segs = basename.rsplit("/",1)
        name = segs[-1]
    
    if(verb > 1): print ('Request for DAG "%s". Reading file %s' % (name, graphml))
    g = nx.read_graphml(graphml)

    if(out):
        print("---- NODES ----")
        print(g.nodes())
        for n in g.nodes():
            print(n)

        print("---- EDGES ----")
        for e in g.edges():
            x = g.edge[e[0]][e[1]]
            print(e,x)


    # f = io.StringIO()
    s = '\n'.join(nx.generate_graphml(g))

    d = Dag(name=name, description=description, graphml=s)
    dagData	= data2post(d).utf8()
    response	= communicate(adddagURL, dagData)
    if(verb>1): print (rdec(response))

    exit(0)
########################################################################
if(add!=''):
    if(name==''):
        name=add

    d ={'dag':add, 'name':name, 'description':description}

    wfData	= data2post(d).utf8()
    response	= communicate(addwfURL, wfData)
    if(verb>1): print (rdec(response))

    exit(0)

###################### GRAND FINALE ####################################
exit(0)
