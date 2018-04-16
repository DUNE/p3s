#!/bin/bash


if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo P3S_INPUT_FILE undefined, exiting
    exit
fi


echo Using input file $P3S_INPUT_FILE

# set up larsoft/duneTPC
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}

# This is in EOS and we'll try to swithc to temp space: cd $P3S_OUTPUT_DIR
cd /tmp

# UUID is set by the pilot,
# and if it is not present at this point,
# we default to a locally generated UUID (mainly the test wrapper case)

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
pwd

# note we should be under /tmp now

if [ -f $P3S_FCL ];
then
    cp $P3S_FCL .
    export P3S_FCL_LOCAL=$(basename $P3S_FCL)
else
    export P3S_FCL_LOCAL=$P3S_FCL
fi
    
env | grep P3S