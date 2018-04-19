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

# UUID should be set by the pilot, and if it is not present at this point,
# we create a locally generated UUID (mainly the test wrapper case)

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

# localize the output to make it easier
# to clean up later.

tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
echo Created a working directory:
pwd

# If the FCL file does not have a valid path,
# we just assume that's a part of duneTPC
# and will be found anyhow

if [ -f $P3S_FCL ];
then
    cp $P3S_FCL .
    export P3S_FCL_LOCAL=$(basename $P3S_FCL)
else
    export P3S_FCL_LOCAL=$P3S_FCL
fi
    
env | grep P3S
