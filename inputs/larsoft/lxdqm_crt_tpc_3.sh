#!/bin/bash

if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo P3S_INPUT_FILE undefined, exiting
    exit
fi

echo Using input file $P3S_INPUT_FILE

# set up larsoft/duneTPC
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/fermilab.opensciencegrid.org/products/larsoft/setups

cd ${P3S_LARSOFT_HOME}
source ${P3S_LARSOFT_RELEASE}/setup
mrbslp
mrbsetenv

# set up the virtual environment
source ${P3S_VENV}/bin/activate

cd $P3S_OUTPUT_DIR

# job uuid is set by the pilot
# if not, default to local uuid - for testing!

export after=''

tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
pwd

cp $P3S_CRT_TXT .

env | grep P3S



if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
    (lar -c $P3S_FCL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_DIR/$tmpdir/lxdqm_crt_tpc_1.root -n $P3S_NEVENTS) 1>$P3S_DATA/joblog/$P3S_JOB_UUID.out 2>$P3S_DATA/joblog/$P3S_JOB_UUID.err
else
    lar -c $P3S_FCL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_DIR/$tmpdir/lxdqm_crt_tpc_1.root -n $P3S_NEVENTS
fi

cp $P3S_DATA/joblog/$P3S_JOB_UUID.out .
cp $P3S_DATA/joblog/$P3S_JOB_UUID.err .
exit
