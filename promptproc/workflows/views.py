###################################################
############ WORKFLOWS VIEWS ######################
###################################################
import json

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


    ### ALL OF THIS WILL NEED TO BE IMPROVED WITH FOREIGN KEYS AND ALL -
    ### WRITTEN THIS WAY TO GET TO SPEED.
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
            # wfVertex.objects.all().delete()
            job.objects.all().delete()
        except:
            success = False
        try:
            # wfEdge.objects.all().delete()
            dataset.objects.all().delete()
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
            # for v in wfVertex.objects.filter(wfuuid=keyname): v.delete()
            for j in job.objects.filter(wfuuid=keyname): j.delete()
        except:
            success = False
        try:
            # for e in wfEdge.objects.filter(wfuuid=keyname): e.delete()
            for ds in dataset.objects.filter(wfuuid=keyname): ds.delete()
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

    fileinfo	= None
    
    post	= request.POST
    dagName	= post['dag']
    name	= post['name']
    state	= post['state']
    filejson	= post['fileinfo']
    description	= post['description']
    wfuuid	= uuid.uuid1()

    if(filejson!=''):
        fileinfo = json.loads(filejson)
    
    ts_def   = timezone.now()

    rootName = dag.objects.get(name=dagName).root

    # Create a Workflow object and populate it:
    wf		= workflow()
    wf.ts_def	= ts_def
    wf.uuid	= wfuuid
    wf.dag	= dagName
    wf.name	= name
    wf.state	= state
    wf.description= description
    # we'll save wf a bit later.

    g = nx.DiGraph()

    # at creation time, the state of objects is set to 'template'
    # and can be toggled to 'defined'

    # Do the jobs
    for dv in dagVertex.objects.filter(dag=dagName):
        g.add_node(dv.name, wf=dagName)
        j = job(
            uuid		= uuid.uuid1(),
            wfuuid		= wfuuid,
            jobtype		= dv.jobtype,
            payload		= dv.payload,
            priority		= dv.priority,
            state		= 'template',
            ts_def		= ts_def,
            timelimit		= dv.timelimit,
            name		= dv.name,
        )

        if(dv.name == rootName): # print("Found root %s %s" %(j.name, j.uuid))
            wf.rootuuid = j.uuid
            
        j.save()
    # ---
    wf.save() # can only do it now since need rootuuid

    # Now do the datasets for the flow
    for de in dagEdge.objects.filter(dag=dagName):

        
        # even in a multigraph, an edge can only be associated with one
        # source and one target. A source and a target can be connected
        # by multiple edges in a multigraph, however. So check for
        # the former condition.
        
        s_cand = job.objects.filter(wfuuid=wfuuid, name=de.source)
        t_cand = job.objects.filter(wfuuid=wfuuid, name=de.target)
        
        if(len(s_cand)!=1): return HttpResponse("addwf: inconsistent graph - source")
        if(len(t_cand)!=1): return HttpResponse("addwf: inconsistent graph - target")
        
        sourceuuid = s_cand[0].uuid
        targetuuid = t_cand[0].uuid

        # a "dataset" - a file in this case - is created by default with a name formed
        # from its UUID and predefined extension (as per type object) - BUT
        # can be overridden by "fileinfo"

        # defaults
        d_uuid	= str(uuid.uuid1())
        dt	= datatype.objects.get(name=de.datatype)
        ext	= dt.ext
        
        dirpath	= de.dirpath
        name	= d_uuid+ext
        comment	= de.comment # default comment

        # Optional overrides: client sends JSON data with "updates"
        if(fileinfo):
            for k in fileinfo.keys():
                if((de.source+":"+de.target)==k):
                    try:
                        name	=fileinfo[k]["name"]
                    except:
                        pass
                    try:
                        dirpath	=fileinfo[k]["dirpath"]
                    except:
                        pass
                    try:
                        comment	=fileinfo[k]["comment"]
                    except:
                        pass
                        
        d = dataset(
            uuid	= d_uuid,
            wfuuid	= wfuuid,
            sourceuuid	= sourceuuid,
            targetuuid	= targetuuid,
            name	= name,
            state	= 'template',
            dirpath	= dirpath,
            comment	= comment,
            datatype	= de.datatype,
            wf     	= name,
        )

        d.save()
        g.add_edge(de.source, de.target)


    if(state=='defined'):wf2defined(wf) # toggles both wf and the root job
    s = '\n'.join(nx.generate_graphml(g))
    return HttpResponse(s)
    
###################################################
def wf2defined(wf):
    wf.state	= 'defined'
    wf.save()
    j = job.objects.get(uuid=wf.rootuuid)
    if(j.jobtype=='noop'):
        # print('root job uuid, noop, toggle to finished',j.uuid)
        j.state = 'finished'
        j.childrenStateToggle('defined')
    else:
        # print('root job uuid, toggle to defined',j.uuid)
        j.state = 'defined'
    j.save()
###################################################
@csrf_exempt
def setwfstate(request):
    post	= request.POST
    wfuuid	= post['uuid']
    state	= post['state']

    wf = workflow.objects.get(uuid=wfuuid)
    
    if(state=='defined'):
        wf2defined(wf)
    else:        
        wf.state=state
        wf.save()
    
    return HttpResponse(state)
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
# d0 = json_graph.node_link_data(g)
# d1= json_graph.adjacency_data(g)
