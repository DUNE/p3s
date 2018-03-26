#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n merge_init -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi


cd $P3S_INPUT_DIR
d=`pwd`

if [ -z ${MERGE_FILE+x} ];
then
    export MERGE_FILE="merge.root"
fi

if [ -z ${NCHAN+x} ];
then
    export NCHAN=100
fi

mf=`find . -name "$MERGE_FILE" 2>/dev/null`
if [ -f "$mf" ]; then
    f=`basename $mf`
    $P3S_HOME/clients/service.py -n merge_init -m "$f exists"
    exit
fi

$P3S_HOME/tools/accumulator.exe init $MERGE_FILE $NCHAN
$P3S_HOME/clients/service.py -n merge_init -m "$MERGE_FILE created with $NCHAN channels"

