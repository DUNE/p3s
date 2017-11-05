#!/bin/sh
Nargs=$#

if [ ! $Nargs -eq 3 ]; then
    echo Wrong number of arguments - expecting 3 - exiting...
    echo Expecting:
    echo \* time window \(minutes\) to trigger on a modified file, needs to be negative for "newer than" and positive for "older than"
    echo \* wildcard or part of it e.g. Proto
    echo \* path to the job template starting with 'input'
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
    #echo $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/$3
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/$3
done

###### Old bits of code for reference
#if [ ! -d "$1" ]; then
#    echo Directory $1 not found, exiting
#    exit 0
#fi
####
#if [ -z "$1" ]; then
#    echo "No time window defined"
#    exit 0
#fi
