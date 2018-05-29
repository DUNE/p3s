#!/bin/bash
export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

echo Sourcing
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
python -V

#source /afs/cern.ch/user/m/mxp/projects/p3s/configuration/p3s_setup.sh

hostname
date
env | grep P3S
env | grep DQM
#ls $P3S_INPUT
#ls $P3S_OUTPUT

echo Activating the script
ls -l $P3S_HOME/clients/evdisp.py

echo 'test test test test test test test test test test test test' > ./adcprep_evt111_ch0-2559.png
echo 'test test test test test test test test test test test test' > ./adcprep_evt111_ch2560-4639.png

cat adcprep_evt111_ch0-2559.png
cat adcprep_evt111_ch2560-4639.png

$P3S_HOME/clients/evdisp.py -a

exit
