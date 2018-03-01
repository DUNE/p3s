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

cd $P3S_OUTPUT_DIR

# job uuid is set by the pilot
# if not, default to local uuid - for testing!

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
# cp $P3S_FCL .
env | grep P3S
lar -c $P3S_FCL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS

dest=$P3S_EVDISP_DIR/$P3S_JOB_UUID

echo making $dest
mkdir $dest
cp *.png $dest

exit
