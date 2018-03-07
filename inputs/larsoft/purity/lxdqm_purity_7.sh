#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}

lar -c $P3S_FCL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENT
ls -l Lifetime_Run1.txt
#source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
#/afs/cern.ch/user/n/np04dqm/public/p3s/scripts/purity.py -f Lifetime_Run1.txt
exit
