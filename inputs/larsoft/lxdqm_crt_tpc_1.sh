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

cd $P3S_DATA/output
# job uuid is set by the pilot
tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
pwd
cp $P3S_CRT_TXT .

env | grep P3S
lar -c $P3S_FCL $P3S_INPUT -T $P3S_OUTPUT/$tmpdir/lxdqm_crt_tpc_1.root
# -n$P3S_NEVENTS
cp $P3S_DATA/joblog/$P3S_JOB_UUID.out .
cp $P3S_DATA/joblog/$P3S_JOB_UUID.err .
exit
