#!/usr/bin/bash
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/fermilab.opensciencegrid.org/products/larsoft/setups
source/afs/cern.ch/user/m/mxp/projects/p3s/configuration/p3s_setup.sh

cd /eos/experiment/neutplatform/protodune/groupdisk/software/ds/
source localProducts_larsoft_v06_38_00_e14_prof/setup
mrbslp

cd $P3S_OUTPUT
p=$$
mkdir $p
cd $p
pwd
env | grep P3S
lar -c $P3S_FCL $P3S_INPUT -T output1.root -n$P3S_NEVENTS
exit
