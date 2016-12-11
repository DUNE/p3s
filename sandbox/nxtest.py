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
    print("---- NODES ----")
    print(g.nodes())
    for n in g.nodes():
        print(n)

print("---- EDGES ----")
for e in g.edges():
    x = g.edge[e[0]][e[1]]
    print(e,x)
    
exit(0)
