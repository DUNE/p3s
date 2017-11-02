#!/bin/sh
Nargs=$#

if [ ! $Nargs -eq 2 ]; then
    echo Wrong number of arguments - expecting 2 - exiting...
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



#if [ ! -d "$1" ]; then
#    echo Directory $1 not found, exiting
#    exit 0
#fi

if [ -z "$1" ]; then
    echo "No time window defined"
    exit 0
fi



cd $P3S_INPUT_DIR
d=`pwd`
echo Directory: $d
files=`find . -maxdepth 1 -mindepth 1 -mmin $1 | sed 's/\.\///'`
echo Files:$files
echo ${#files[@]}
for f in $files
do
    echo ! $f
    echo $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/$2
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/$2
done
