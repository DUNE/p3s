from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt

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
def adddag(request):
    
    post	= request.POST

    name	= post['name']
    graphml	= post['graphml']
    description	= post['description']

    print(name)

    d = None
    try: # cleanout: names are unique
        d = dag.objects.get(name=name)
        d.delete()
        for v in dagVertex.objects.filter(dag=name):	v.delete()
        for e in dagEdge.objects.filter(dag=name):	e.delete()
    except:
        pass

    newDag = dag()
    newDag.name = name
    newDag.description = description

    newDag.save()
    fn = "/tmp/p3s/"+name+".graphml"
    f = open(fn, "w") # FXIME: this has yet to work: f = io.StringIO()
    f.write(graphml)
    f.close()

    print(graphml)
    
    f = open(fn, "r")
    g = nx.read_graphml(f)

    for n in g.nodes(data=True):
        print(n)
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

    # print("---------------")
    # d0 = json_graph.node_link_data(g)
    # print(d0)
    # print("---------------")
    # d1= json_graph.adjacency_data(g)
    # print(d1)
    # print("---------------")

