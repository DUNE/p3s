###################################################
############ WORKFLOWS VIEWS ######################
###################################################
from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone

import io
import uuid
import networkx as nx
from networkx.readwrite import json_graph

from .models import dag, dagVertex, dagEdge
from .models import workflow, wfVertex, wfEdge

from jobs.models			import job
from data.models			import dataset, datatype

def init(request):
    d = dag(name='test')
    if(dag._init):
        status = 'initialized'
    else:
        status = 'not initialized'
    dag._init = True
    return HttpResponse("WF INIT %s %s" % (d, status))

###################################################
# SHOULD ONLY BE USED BY EXPERTS, do not advertise
def deleteall(request):
    what = request.GET.get('what','')
    if(what==''):
        return HttpResponse("DELETE ALL: SPECIFICATION OF OBJECTS TO BE DELETED MISSING")

    success = True
    if(what=='dag'): 
        try:
            dag.objects.all().delete()
        except:
            success = False
        try:
            dagVertex.objects.all().delete()
        except:
            success = False
        try:
            dagEdge.objects.all().delete()
        except:
            success = False

    if(what=='workflow'): 
        try:
            wfVertex.objects.all().delete()
        except:
            success = False
        try:
            wfEdge.objects.all().delete()
        except:
            success = False
        try:
            workflow.objects.all().delete()
        except:
            success = False

    if(success):
        return HttpResponse("Deleted ALL %s" % what )
    else:
        return HttpResponse("Problems deleting ALL %s" % what )


###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    what	= post['what']
    
    keyname	= ''
    
    success = True
    
    if(what=='dag'):
        keyname = post['name']
        success	= deldag(keyname)

    if(what=='workflow'):
        keyname	= post['uuid']
        try:
            w = workflow.objects.get(uuid=keyname)
            w.delete()
        except:
            success = False
        try:
            for v in wfVertex.objects.filter(wfuuid=keyname): v.delete()
        except:
            success = False
        try:
            for e in wfEdge.objects.filter(wfuuid=keyname): e.delete()
        except:
            success = False

    if(success):
        return HttpResponse("Deleted %s %s" % (what, keyname) )
    else:
        return HttpResponse("Problems deleting %s %s" % (what, keyname) )

###################################################
def deldag(name):
    success = True
    try:
        d = dag.objects.get(name=name)
        d.delete()
    except:
        success = False
    try:
        for v in dagVertex.objects.filter(dag=name): v.delete()
    except:
        success = False
    try:
        for e in dagEdge.objects.filter(dag=name): e.delete()
    except:
        success = False
        
    return success
###################################################
@csrf_exempt
def adddag(request):
    
    post	= request.POST

    name	= post['name']
    graphml	= post['graphml']
    description	= post['description']

    x = deldag(name)
    
    fn = "/tmp/p3s/"+name+".graphml"
    f = open(fn, "w") # FXIME: this has yet to work: f = io.StringIO()
    f.write(graphml)
    f.close()

    
    f = open(fn, "r")
    g = nx.read_graphml(f)

    ts_def   = timezone.now()
    vertices = nx.topological_sort(g)
    print('*****',vertices)
    
    newDag		= dag()
    newDag.name		= name
    newDag.description	= description
    newDag.nvertices	= len(vertices)
    newDag.ts_def	= ts_def
    newDag.root		= vertices[0]
    newDag.save()

    dvFields = []
    for f in dagVertex._meta.get_fields():dvFields.append(f.name)
    for n in g.nodes(data=True):# print(n)
        dv = dagVertex()
        dv.name  = n[0]
        dv.dag   = name
        dicto = n[1]
        for k in dicto.keys():
            if k in dvFields:
                dv.__dict__[k]=dicto[k]
        dv.save()
        
    deFields = []
    for f in dagEdge._meta.get_fields():deFields.append(f.name)
    print(deFields)
    for e in g.edges(data=True):
        print(e)
        de = dagEdge()
        de.source = e[0]
        de.target = e[1]
        de.name	  = e[2]['name']
        de.dag    = name
        dicto = e[2]
        for k in dicto.keys():
            if k in deFields:
                de.__dict__[k]=dicto[k]
        de.save()

    return HttpResponse("RESPONSE %s" % graphml )

###################################################
@csrf_exempt
def addwf(request):
    
    post	= request.POST
    dagName	= post['dag']
    name	= post['name']
    description	= post['description']
    wfuuid	= uuid.uuid1()

    ts_def   = timezone.now()

    rootName = dag.objects.get(name=dagName).root

    # Create a Workflow object and populate it:
    wf		= workflow()
    wf.ts_def	= ts_def
    wf.uuid	= wfuuid
    wf.dag	= dagName
    wf.name	= name
    wf.description= description

    g = nx.DiGraph()

    for dv in dagVertex.objects.filter(dag=dagName):
        g.add_node(dv.name, wf=dagName)

        # NEW
        j = job(
            uuid		= uuid.uuid1(),
            wfuuid		= wfuuid,
            jobtype		= dv.jobtype,
            payload		= dv.payload,
            priority		= dv.priority,
            state		= 'template', # FIXME
            ts_def		= ts_def,
            timelimit		= dv.timelimit,
            name		= dv.name,
        )

        if(dv.name == rootName):
            print("Found root %s %s" %(j.name, j.uuid))
        j.save()

       
    wf.save() # can only do it now since need rootuuid
    
    for de in dagEdge.objects.filter(dag=dagName):
        # NEW
        d = dataset(
            uuid	= uuid.uuid1(),
            wfuuid	= wfuuid,
            name	= de.name,
            state	= 'template',
            comment	= de.comment,
            datatype	= de.datatype,
            wf     	= '',
        )

        d.save()

        # name	= de.name
        # we	= wfEdge()
        # we.name	= name
        # we.wfuuid= wfuuid
        # we.source = de.source
        # we.target = de.target
        # we.wf	= wf.name
        # we.save()
        g.add_edge(de.source, de.target)

    s = '\n'.join(nx.generate_graphml(g))
    return HttpResponse(s)
    
###################################################
def getdag(request):
    name = request.GET.get('name','')

    if(name == ''): return HttpResponse("DAG not specified.")
    g = fetchdag(name)
    s = '\n'.join(nx.generate_graphml(g))
    return HttpResponse(s)

###################################################
def fetchdag(dag): # inflate DAG from RDBMS
    g = nx.DiGraph()
    
    for dv in dagVertex.objects.filter(dag=dag):
        g.add_node(dv.name)
        
    for de in dagEdge.objects.filter(dag=dag):
        g.add_edge(de.source, de.target)

    return g


################ DUSTY ATTIC ######################
    # print("---------------")
    # d0 = json_graph.node_link_data(g)
    # print(d0)
    # print("---------------")
    # d1= json_graph.adjacency_data(g)
    # print(d1)
    # print("---------------")

        # wv	= wfVertex()
        # wv.name	= name
        # wv.wf	= wf.name
        # wv.wfuuid= wfuuid
        # wv.save()
