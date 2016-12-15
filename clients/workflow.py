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
from comms		import data2post


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
                    help="GraphML file to be read and parsed, to then create a DAG on the server.")

parser.add_argument("-n", "--name",	type=str,	default='',
                    help="The name of the DAG or workflow to be manipulated, depending on the context.")

parser.add_argument("-a", "--add",	type=str,	default='',
                    help='''Add a workflow. Argument is the name of the prototype DAG (stored on the server).
                    If no special name is provided for the workflow via the *name* argument, defaults to the DAG name''')

parser.add_argument("-D", "--description",	type=str,	default='',
                    help="Description of the DAG or workflow.")

parser.add_argument("-o", "--out",	action='store_true',
                    help="output the graph to stdout")

parser.add_argument("-G", "--get",	action='store_true',
                    help="get a DAG from server, needs the name")


parser.add_argument("-H", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a dag. Needs name.")


##########################
parser.add_argument("-s", "--state",	type=str,	default='',
                    help="sets the job state, needs *adjust* option to be activated")

parser.add_argument("-p", "--priority",	type=int,	default=-1,
                    help="sets the job priority, needs *adjust* option to be activated")


parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the job to be adjusted (pk)")
parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, forms a request but does not contact the server")
parser.add_argument("-v", "--verbosity",	type=int, default=0, choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file from which to read job templates (must be a list)")

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage

server	= args.server
state	= args.state
priority= args.priority

j_id	= args.id
verb	= args.verbosity
tst	= args.test
add	= args.add
delete	= args.delete

get	= args.get
name	= args.name
graphml	= args.graphml
description = args.description
out	= args.out

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
wfList = []

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

###################### DAG DELETE ######################################
# Check if it was a deletion request
if(delete):
    response = None
    if(name==''): exit(-1) # check if we have the key

    # DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(name=='ALL'): # FIXME - not implemented, see "normal delete" which works
        try:
            url = 'workflows/deleteall'
            response = urllib.request.urlopen(server+url) # GET
        except URLError:
            exit(1)

        data = response.read()
        if(verb >0): print (data)

    # Normal delete
    if ',' in name: # assume we have a CSV list
        wfList = name.split(',')
    else:
        wfList.append(name)

    for w in wfList:
        delData = data2post(dict(name=w)).utf8()

        try:
            url = 'workflows/deletedag'
            response = urllib.request.urlopen(server+url, delData) # POST
        except URLError:
            exit(1)
    
        data = response.read()
        if(verb >0): print (data)

    exit(0)

########################################################################
if(get):
    response = None
    if(name==''): exit(-1) # check if we have the key
    try:
        url = 'workflows/getdag?name='+name
        response = urllib.request.urlopen(server+url) # GET
    except URLError:
        exit(1)
    
    data = response.read().decode("utf-8") 
    print (data)
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
    dagData = data2post(d).utf8()
    
    try:
        url = 'workflows/adddag'
        response = urllib.request.urlopen(server+url, dagData) # POST
    except URLError:
        exit(1)
    
    data = response.read()
    if(out): print (data)

    exit(0)
########################################################################
if(add!=''):
    if(name==''):
        name=add

    d ={'dag':add, 'name':name, 'description':description}
    wfData = data2post(d).utf8()
    try:
        url = 'workflows/addworkflow'
        response = urllib.request.urlopen(server+url, wfData) # POST
    except URLError:
        exit(1)
    
    data = response.read().decode("utf-8") 
    if(out): print (data)

    exit(0)

###################### GRAND FINALE ####################################
exit(0)
