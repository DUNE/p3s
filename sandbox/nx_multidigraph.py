import argparse
import networkx as nx
from networkx.readwrite import json_graph
import io
from io import StringIO

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

g = nx.DiGraph()
g.add_node("foo")
g.add_node("moo")
g.add_node("goo")
g.add_node("shoo")

g.add_edge("foo","moo")
g.add_edge("foo","goo")

g.add_edge("goo","shoo")
g.add_edge("moo","shoo")


efm = g.edge["foo"]["moo"]
efm['resistance']=10
# efm['id']='efm'
    

g.node['foo']['voltage']=220
g.node['foo']['current']=10

g.node['moo']['current']=5
g.node['moo']['voltage']=110

print("---------------")
d0 = json_graph.node_link_data(g)
print(d0)
print("---------------")
d1= json_graph.adjacency_data(g)
print(d1)
print("---------------")

f = io.StringIO()
s = '\n'.join(nx.generate_graphml(g))

print(s)
f.write(s)

G = nx.read_graphml(f)
