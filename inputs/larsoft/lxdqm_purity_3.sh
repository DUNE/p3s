#!/bin/bash

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
tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
pwd
cp $P3S_FCL_DIR/$P3S_FCL .
env | grep P3S
lar -c $P3S_FCL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS
exit
