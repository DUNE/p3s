#!/bin/bash
export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

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

$P3S_HOME/clients/evdisp.py -h

exit
