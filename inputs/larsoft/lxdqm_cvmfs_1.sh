#!/bin/bash

export DUNETPCVER='v06_69_00'
export DUNETPCQUAL='e15:prof'
export NUMEVENTS=1
export INPUTFILE=/eos/experiment/neutplatform/protodune/np04tier0/p3s/testinput/ProtoDUNE_beam_-7GeV_cosmics_3ms_sce_99_20170719T222727_merged0_25712_1510288920487.root

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}

lar -n ${NUMEVENTS} -c dump_hits.fcl ${INPUTFILE}
ofn=`basename ${INPUTFILE}`_DumpHits.log

mv DumpHits.log ${ofn}
#gzip ${ofn}
#cp ${ofn}.gz ${OUTPUTDIR}
