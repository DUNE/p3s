#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

export P3S_INPUT_DIR=$P3S_DIRPATH/input

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n ped_emu -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi

env | grep P3
cd $P3S_INPUT_DIR
d=`pwd`
echo Directory: $d

$P3S_HOME/tools/pedestal_emulator.exe ped${P3S_JOB_UUID}.root $ENTRIES $NCHAN

