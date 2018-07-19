#!/usr/bin/env python
from __future__ import print_function
import os, sys, time

def main(input_rootfile, output_jsonfile):
    rootIndex = output_jsonfile.find('protodune-live') - 1
    assert(rootIndex>0)
    rootDir = output_jsonfile[:rootIndex]
    assert(os.path.exists(rootDir))
    # print(rootDir)

    dirname, basename = os.path.split(output_jsonfile)
    # print(dirname, basename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    cmd = "root -b -q -l loadClasses.C 'run.C(\"%s\", \"%s\")'" % (
        input_rootfile,
        output_jsonfile)
    print(cmd)
    while (True):
        os.system(cmd)
        time.sleep(10)


def usage():
    print("""
    python dump_json.py [input_rootfile] [output_jsonfile]

    """)

if __name__ == "__main__":
    if (len(sys.argv)<=1):
        usage()
    else:
        main(sys.argv[1], sys.argv[2])