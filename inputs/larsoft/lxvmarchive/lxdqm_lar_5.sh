#!/bin/bash

# set up larsoft/duneTPC
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/fermilab.opensciencegrid.org/products/larsoft/setups

cd ${P3S_LARSOFT_HOME}
source ${P3S_LARSOFT_RELEASE}/setup
mrbslp

# set up the virtual environment
source ${P3S_VENV}/bin/activate

cd $P3S_OUTPUT
p=$$
mkdir $p
cd $p
pwd
cp $P3S_FCL_AUX .
env | grep P3S
lar -c $P3S_FCL $P3S_INPUT -T output1.root -n$P3S_NEVENTS
exit
