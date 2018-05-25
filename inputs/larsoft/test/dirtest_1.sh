#!/bin/bash
echo Sourcing
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
python -V
python3.5 -V
#source /afs/cern.ch/user/m/mxp/projects/p3s/configuration/p3s_setup.sh

hostname
date
env | grep P3S
env | grep DQM
#ls $P3S_INPUT
#ls $P3S_OUTPUT
exit
