#!/bin/sh

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}

lar -n ${NUMEVENTS} -c dump_hits.fcl ${INPUTFILE}
ofn=`basename ${INPUTFILE}`_DumpHits.log

mv DumpHits.log ${OUTPUTDIR}/${ofn}

