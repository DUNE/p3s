from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt

import io
import networkx as nx
from networkx.readwrite import json_graph

from .models import dag

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
    graphml	= post['graphml']

    ### print(graphml)

    f = open("/tmp/p3s/graphml.buf", "w")
    # FXIME: this has yet to wotk   f = io.StringIO()
    f.write(graphml)
    f.close()
    
    f = open("/tmp/p3s/graphml.buf", "r")
    g = nx.read_graphml(f)
    
    print("---------------")
    d0 = json_graph.node_link_data(g)
    print(d0)
    print("---------------")
    d1= json_graph.adjacency_data(g)
    print(d1)
    print("---------------")

    return HttpResponse("RESPONSE %s" % graphml )
