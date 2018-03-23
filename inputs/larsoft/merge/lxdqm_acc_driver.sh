#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
source $P3S_HOME/inputs/larsoft/setup_env_np04dqm.sh

export P3S_INPUT_DIR=$P3S_DIRPATH/input
export P3S_MERGE_DIR=$P3S_DIRPATH/merge

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n acc_init -m "Problem with the directory $P3S_INPUT_DIR"
    exit 1
fi

cd $P3S_INPUT_DIR

d=`pwd`

files=`find . -maxdepth 1 -mindepth 1 -size +1 -name "ped*" | sed 's/\.\///'`

COUNTER=0

export MERGE_FACTOR=5

while [ $COUNTER -lt 150 ]; do
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
	$P3S_HOME/tools/accumulator.exe add merge.root $f

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
done

echo number of files merged - $COUNTER

# create a timestamp-based filename for the merge file
ts=`date -d "today" +"%Y%m%d%H%M"`
mergefile=merge$ts.root
# move the merge to the final location
mv merge.root ../merge/$mergefile

# register the merged file with p3s using the appropriate client:
argument='{"name":"'$mergefile'","state":"defined","comment":"merged_histograms","datatype":"MERGE","dirpath":"'$P3S_MERGE_DIR'"}'
$P3S_HOME/clients/dataset.py -r -j $argument

exit

# ta-dah!


# Dev notes:
# If we used the line below  to run jobs, it would result in an asynchronous operation of these jobs in p3s
# so the merge file could be in an inconsistent state.
#
# $P3S_HOME/clients/dataset.py -v 0 -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/merge/lxdqm_acc_add_2.json
#
# For this reason we revert to a synchronous loop.

