#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

export P3S_INPUT_DIR=$P3S_DIRPATH/input

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n acc_init -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi

cd $P3S_INPUT_DIR

d=`pwd`

files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`

COUNTER=0

export MERGE_FACTOR=3

while [ $COUNTER -lt 150 ]; do
    files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`
    for f in $files
    do
	echo $f
	# $P3S_HOME/clients/dataset.py -v 0 -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/merge/lxdqm_acc_add_2.json
	argument='{"name":"'$f'","state":"defined","comment":"testing with text files", "datatype":"TXT","dirpath":"'$P3S_INPUT_DIR'"}'
	$P3S_HOME/clients/dataset.py -r -j $argument
	$P3S_HOME/tools/accumulator.exe add merge.root $f
	let COUNTER+=1
	if [ $COUNTER -ge $MERGE_FACTOR ]; then
	    break
	fi
    done
    if [ $COUNTER -ge $MERGE_FACTOR ]; then
	break
    fi
done
echo $COUNTER
ts=`date -d "today" +"%Y%m%d%H%M"`
mv merge.root ../merge/merge$ts.root
