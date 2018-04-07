#!/bin/sh

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi

source ${P3S_LAR_SETUP}

lar -n ${P3S_NEVENTS} -c dump_hits.fcl ${P3S_INPUT_FILE}

ofn=`basename ${P3S_INPUT_FILE}`_DumpHits_${P3S_JOB_UUID}.log

mv DumpHits.log ${OUTPUTDIR}/${ofn}

