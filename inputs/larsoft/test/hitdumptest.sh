#!/bin/sh

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}

lar -n ${NUMEVENTS} -c dump_hits.fcl ${INPUTFILE}

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

ofn=`basename ${INPUTFILE}`_DumpHits_${P3S_JOB_UUID}.log

mv DumpHits.log ${OUTPUTDIR}/${ofn}

