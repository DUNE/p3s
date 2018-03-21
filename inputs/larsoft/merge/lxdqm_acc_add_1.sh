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
merge_file=`find . -maxdepth 1 -mindepth 1 -size +1 -name "merge*" | sed 's/\.\///'`

echo $merge_file

# $P3S_HOME/tools/accumulator.exe add $MERGE_FILE $P3S_INPUT_FILE

# $P3S_HOME/clients/service.py -n acc_init -m "Merge file created"

