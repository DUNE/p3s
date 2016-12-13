from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone

import io
import networkx as nx
from networkx.readwrite import json_graph

from .models import dag, dagVertex, dagEdge


def init(request):
    d = dag(name='test')
    if(dag._init):
        status = 'initialized'
    else:
        status = 'not initialized'
    dag._init = True
    return HttpResponse("WF INIT %s %s" % (d, status))

###################################################
@csrf_exempt
def delete(request):
    
    post	= request.POST
    name	= post['name']

    try:
        d = dag.objects.get(name=name)
        d.delete()
        for v in dagVertex.objects.filter(dag=name):	v.delete()
        for e in dagEdge.objects.filter(dag=name):	e.delete()
        return HttpResponse("Deleted DAG %s" % name )
    except:
        return HttpResponse("Failed to delete DAG %s" % name )

###################################################
@csrf_exempt
def adddag(request):
    
    post	= request.POST

    name	= post['name']
    graphml	= post['graphml']
    description	= post['description']

    print(name)
    x = delete(request)
    
    fn = "/tmp/p3s/"+name+".graphml"
    f = open(fn, "w") # FXIME: this has yet to work: f = io.StringIO()
    f.write(graphml)
    f.close()

    
    f = open(fn, "r")
    g = nx.read_graphml(f)

    ts_def   = timezone.now()
    
    vertices = nx.topological_sort(g)

    newDag		= dag()
    newDag.name		= name
    newDag.description	= description
    newDag.nvertices	= len(vertices)
    newDag.ts_def	= ts_def
    newDag.root		= vertices[0]
    newDag.save()

    for n in g.nodes(data=True):
        #        print(n)
        dv = dagVertex()
        dv.name  = n[0]
        dv.dag   = name
        dv.save()
        
    for e in g.edges(data=True):
        #        print(e)
        de = dagEdge()
        de.source = e[0]
        de.target = e[1]
        de.name	  = e[2]['name']
        de.dag    = name
        de.save()
    return HttpResponse("RESPONSE %s" % graphml )

###################################################
@csrf_exempt
def addworkflow(request):
    
    post	= request.POST
    dag		= post['dag']
    
    wf_uuid	= uuid.uuid1()

    return HttpResponse("RESPONSE %s" % dag )
    
###################################################
def getdag(request):
    name = request.GET.get('name','')

    if(name == ''):
        return HttpResponse("DAG not specified.")
    
    print(name)
    for de in dagEdge.objects.filter(dag=name):
        print(de)

    return HttpResponse("")

    # print("---------------")
    # d0 = json_graph.node_link_data(g)
    # print(d0)
    # print("---------------")
    # d1= json_graph.adjacency_data(g)
    # print(d1)
    # print("---------------")

