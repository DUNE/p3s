#!/usr/bin/bash
source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /cvmfs/fermilab.opensciencegrid.org/products/larsoft/setups
source /mnt/nas01/users/mxp/projects/p3s/configuration/p3s_setup.sh

cd /mnt/nas01/software/dqm/larsoft/v06
source localProducts_larsoft_v06_33_00_e14_prof/setup
mrbslp
cd $P3S_DIRPATH
p=$$
mkdir $p
cd $p
pwd

lar -c /mnt/nas01/users/mxp/projects/p3s/inputs/larsoft/neutdqm_lar_2.fcl /mnt/nas01/users/radescu/Feb2017_v22/inputs/detsim_single_DistONSuppOFF_100.root -T output.root -n50
exit
