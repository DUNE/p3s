#!/bin/sh


export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

export P3S_INPUT_DIR=$P3S_DIRPATH/input
export P3S_MERGE_DIR=$P3S_DIRPATH/merge
export P3S_PED_DIR=$P3S_DIRPATH/pedestals

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n merge_add -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi

cd $P3S_INPUT_DIR
d=`pwd`

$P3S_HOME/tools/accumulator.exe add merge.root $P3S_INPUT_FILE
$P3S_HOME/clients/service.py -n merge_add -m "Merged $P3S_INPUT_FILE"

