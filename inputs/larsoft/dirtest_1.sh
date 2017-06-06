#!/bin/bash
echo Sourcing
source/afs/cern.ch/user/m/mxp/vp3s/bin/activate
python -V
source/afs/cern.ch/user/m/mxp/projects/p3s/configuration/p3s_setup.sh

hostname
date
env | grep P3S
ls $P3S_INPUT
ls $P3S_OUTPUT
exit
