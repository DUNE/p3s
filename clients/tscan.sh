#!/bin/sh
Nargs=$#

if [ ! $Nargs -eq 2 ]; then
    echo Wrong number of arguments - expecting 2 - exiting...
    echo Expecting:
    echo \* time window \(minutes\) to trigger on a modified file, needs to be negative for "newer than" and positive for "older than"
    echo \* wildcard or part of it e.g. Proto
    exit
fi


if [ "${P3S_SITE}" = 'lxvm' ]
then
    echo Activating venv at lxvm
    source /afs/cern.ch/user/m/mxp/vp3s/bin/activate
    export P3S_HOME=/afs/cern.ch/user/m/mxp/projects/p3s
    export P3S_INPUT_DIR=$P3S_DIRPATH/input
else
    echo Assuming site sagebrush
    export P3S_HOME=/home/maxim/projects/p3s
    export P3S_INPUT_DIR=$P3S_DIRPATH/p3sdata/input
fi
# exit 0



cd $P3S_INPUT_DIR
d=`pwd`
echo Directory: $d
files=`find . -maxdepth 1 -mindepth 1 -mmin $1 -name "$2*" | sed 's/\.\///'`
echo Files:$files
# echo ${#files[@]}

# exit 0

for f in $files
do
    echo ! $f
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/lxdqm_evdisp_4.json -N
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/lxdqm_crt_tpc_3.json -N
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/inputs/larsoft/lxdqm_purity_5.json
done
