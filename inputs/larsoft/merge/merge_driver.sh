#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

export P3S_INPUT_DIR=$P3S_DIRPATH/input
export P3S_MERGE_DIR=$P3S_DIRPATH/merge
export P3S_PED_DIR=$P3S_DIRPATH/pedestals


# declare this once!
# AND fix the ugly later

if [ -z ${MERGE_FILE+x} ];
then
    export MERGE_FILE="merge.root"
fi

if [ -z ${NCHAN+x} ];
then
    export NCHAN=100
fi

if [ -z ${MERGE_FACTOR+x} ];
then
    export MERGE_FACTOR=5
fi

if [ -z ${SLEEP+x} ];
then
    export SLEEP=10
fi


if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n merge_add -m "Problem with the directory $P3S_INPUT_DIR"
    exit 1
fi

cd $P3S_INPUT_DIR

d=`pwd`

# check if we have the merge file
if [ ! -f "$MERGE_FILE" ]; then
    echo $MERGE_FILE not detected, will be created
    $P3S_HOME/tools/accumulator.exe init $MERGE_FILE $NCHAN
    $P3S_HOME/clients/service.py -n merge_init -m "$MERGE_FILE created with $NCHAN channels"
fi

# detect potential files for merging
files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`

# a counter for the files that were merged
COUNTER=0

while [ $COUNTER -lt $MERGE_FACTOR ]; do
    files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`
    for f in $files
    do
	q=`$P3S_HOME/clients/dataset.py -G -f $f`

	# check if this file was already accounted for, skip it then
	if [ $q != "[]" ]; then continue; fi
	
	echo merging $f in $d
	    
	# register this file with p3s using the appropriate client:
	argument='{"name":"'$f'","state":"defined","comment":"histograms","datatype":"MERGEINPUT","dirpath":"'$P3S_INPUT_DIR'"}'
	$P3S_HOME/clients/dataset.py -r -j $argument
	
	# do the merge:
	$P3S_HOME/tools/accumulator.exe add $MERGE_FILE $f
	if [ $? -ne 0 ]; then
	    $P3S_HOME/clients/service.py -n merge_add -m "problem merging $f"
	    mv $f P3S_PED_DIR
	fi

	mv $f $P3S_PED_DIR
	
	# check if merged enough files
	let COUNTER+=1
	if [ $COUNTER -ge $MERGE_FACTOR ]; then
	    break
	fi
    done

    # if enough files were merged, just finalize the result and exit
    if [ $COUNTER -ge $MERGE_FACTOR ]; then
	break
    fi
    # if we came here, this means more statistics are needed. Wait and re-enter the loop
    sleep $SLEEP
done

echo $COUNTER files merged

# create a timestamp-based filename for the merge file, move the merge to the final location
ts=`date -d "today" +"%Y%m%d%H%M"`
mergefile=merge$ts.root
mv $MERGE_FILE ../merge/$mergefile

# register the merged file with p3s using the appropriate client:
argument='{"name":"'$mergefile'","state":"defined","comment":"merged_histograms","datatype":"MERGE","dirpath":"'$P3S_MERGE_DIR'"}'
$P3S_HOME/clients/dataset.py -r -j $argument

$P3S_HOME/clients/service.py -n merge_add -m "Merge file created: $mergefile in $P3S_MERGE_DIR"


exit
# ta-dah!


# Dev notes:
# If we used the line below  to run jobs, it would result in an asynchronous operation of these jobs in p3s
# so the merge file could be in an inconsistent state.
#
# $P3S_HOME/clients/dataset.py -v 0 -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/merge/lxdqm_acc_add_2.json
#
# For this reason we revert to a synchronous loop.

