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

files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`

COUNTER=0
while [ $COUNTER -lt 150 ]; do
    files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`
    for f in $files
    do
	echo $f
	echo $P3S_HOME/tools/accumulator.exe add merge.root $f
	let COUNTER+=1
	if [ $COUNTER -ge 150 ]; then
	    break
	fi
    done
    if [ $COUNTER -ge 150 ]; then
	break
    fi
done
echo $COUNTER

