#!/bin/bash


if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo P3S_INPUT_FILE undefined, exiting
    exit
fi


echo Using input file $P3S_INPUT_FILE

# set up larsoft/duneTPC
if [ -z ${P3S_AFS_SETUP+x} ];
then
    echo Will use CVMFS setup
    source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
else
    echo Will use AFS setup
    source ${P3S_AFS_SETUP}/dunetpc_${DUNETPCVER}/products/setup
fi

setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}

echo Checking lar
which lar
lar -h

retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error: larsoft not found"
    exit $retVal
fi

finished checking lar

# UUID should be set by the pilot, and if it is not present at this point,
# we create a locally generated UUID (mainly the test wrapper case)

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

# localize the output to make it easier to clean up later.

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

echo lar_setup_2 finished

