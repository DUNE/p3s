import argparse
import networkx as nx
from networkx.readwrite import json_graph

#########################################################################
parser = argparse.ArgumentParser()

parser.add_argument("-g", "--graphml",	type=str,	default='',
                    help="GraphML file to be read and parsed.")

parser.add_argument("-o", "--out",	action='store_true',
                    help="output the graph to stdout")
########################### Parse all arguments #########################
args = parser.parse_args()
graphml	= args.graphml
out	= args.out

g = None # the graph we are going to experiment with

if(graphml!=''):
    g = nx.read_graphml("t.graphml")

if(out):
    print(g.nodes())
    print(g.edges())
    
exit(0)


g = nx.DiGraph()
g.add_node("foo")
g.add_node("moo")
g.add_node("goo")

g.add_edge("foo","moo")
g.add_edge("foo","goo")

g.node['foo']['voltage']=220
g.node['foo']['current']=10

g.node['moo']['current']=5
g.node['moo']['voltage']=110

d = json_graph.node_link_data(g)
print(d)

h = json_graph.node_link_graph(d)

print("---------------")
print(h)



print(h.nodes())
