#!/usr/bin/bash
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/fermilab.opensciencegrid.org/products/larsoft/setups
source /mnt/nas01/users/mxp/projects/p3s/configuration/p3s_setup.sh

cd /mnt/nas01/software/dqm/larsoft/v06
source localProducts_larsoft_v06_33_00_e14_prof/setup
mrbslp
cd $P3S_OUTPUT
p=$$
mkdir $p
cd $p
pwd
env | grep P3S
lar -c $P3S_FCL $P3S_INPUT -T output1.root -n$P3S_NEVENTS
exit
