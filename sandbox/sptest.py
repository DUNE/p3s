import argparse
import subprocess
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

x=subprocess.run(["date"], stdout=subprocess.PIPE)

print(x.stdout.decode("utf-8"))

x=subprocess.run(["true"], stdout=subprocess.PIPE)

print(x.stdout.decode("utf-8"))

exit(0)
