#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

source $P3S_HOME/configuration/lxvm_np04dqm.sh > /dev/null

source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate

export P3S_INPUT_DIR=$P3S_DIRPATH/input

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n ped_emu -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi

env | grep P3
cd $P3S_INPUT_DIR
d=`pwd`
echo Directory: $d
num=`uuid`
$P3S_HOME/tools/pedestal_emulator.exe ped$num.root $ENTRIES $NCHAN

