#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

source $P3S_HOME/configuration/lxvm_np04dqm.sh > /dev/null

source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate

export P3S_INPUT_DIR=$P3S_DIRPATH/input

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n acc_init -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi


cd $P3S_INPUT_DIR
d=`pwd`

if [ -z ${MERGE_FILE+x} ];
then
    export MERGE_FILE="merge_0.root"
fi

if [ -z ${NCHAN+x} ];
then
    export NCHAN=100
fi

mf=`find . -name "merge_*" 2>/dev/null`
if [ -f "$mf" ]; then
    $P3S_HOME/clients/service.py -n acc_init -m "Merge file $mf exists"
    exit
fi

echo Parameters: $MERGE_FILE $NCHAN

$P3S_HOME/tools/accumulator.exe init $MERGE_FILE $NCHAN
$P3S_HOME/clients/service.py -n acc_init -m "Merge file $MERGE_FILE created"

