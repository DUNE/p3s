#!/usr/bin/env python3
import argparse
import networkx as nx
from networkx.readwrite import json_graph
import io
from io import StringIO

#########################################################################
parser = argparse.ArgumentParser()

parser.add_argument("-m", "--multi",	action='store_true',
                    help="use multigraph")

parser.add_argument("-g", "--graphml",	type=str,	default='',
                    help="GraphML file to be read and parsed (future dev).")

parser.add_argument("-o", "--out",	type=str,	default='',
                    help="if defined, the name of GraphML file to be generated.")

parser.add_argument("-p", "--print",	action='store_true',
                    help="output the graph to stdout as graphml")

parser.add_argument("-j", "--json",	action='store_true',
                    help="output the graph to stdout as json link and adjacency data")
########################### Parse all arguments #########################
args	= parser.parse_args()
graphml	= args.graphml
prGraph	= args.print
multi	= args.multi
json	= args.json
out	= args.out

if(multi):
    g = nx.MultiDiGraph()
    g.add_node("foo")
    g.add_node("moo")
    
    g.node['foo']['voltage']=220

    g.add_edge("foo","moo",key='ready')
    g.add_edge("foo","moo",key='set')
    g.add_edge("foo","moo",key='go', rules="reglement")

    e = g.edge["foo"]["moo"]["ready"]
    e["resistance"] = "futile"

else:
    g = nx.DiGraph()

    g.add_node("foo")
    g.node['foo']['voltage']=220
    g.add_node("moo")
    g.add_node("goo")
    g.add_node("shoo")

    g.add_edge("foo","moo")
    g.add_edge("foo","goo")
    g.add_edge("goo","shoo")
    g.add_edge("moo","shoo")

    efm = g.edge["foo"]["moo"]
    efm['resistance']=10
    g.node['foo']['voltage']=220
    g.node['foo']['current']=10
    g.node['moo']['current']=5
    g.node['moo']['voltage']=110

    

if(out!=''):
    nx.write_graphml(g, out)
    
if(json):
    print("---------------LINK DATA------------------")
    d0 = json_graph.node_link_data(g)
    print(d0)
    print("------------ADJACENCY DATA----------------")
    d1= json_graph.adjacency_data(g)
    print(d1)
    print("------------------------------------------")

if(prGraph):
    s = '\n'.join(nx.generate_graphml(g))
    print(s)
