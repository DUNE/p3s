import networkx as nx
from networkx.readwrite import json_graph

#g = nx.read_graphml("t.graphml")
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
