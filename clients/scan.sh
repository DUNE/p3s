#!/bin/sh
Nargs=$#

if [ ! $Nargs -eq 3 ]; then
    echo Wrong number of arguments - expecting 3 - exiting...
    exit
fi


if [ "${P3S_SITE}" = 'lxvm' ]
then
    echo Activating venv at lxvm
    source /afs/cern.ch/user/m/mxp/vp3s/bin/activate
fi

# exit 0



if [ ! -d "$1" ]; then
    echo Directory $1 not found, exiting
    exit 0
fi

if [ -z "$2" ]; then
    echo "No time window defined"
    exit 0
fi


export P3S_HOME=/home/maxim/projects/p3s

cd $1
d=`pwd`
echo Directory: $d
files=`find . -maxdepth 1 -mindepth 1 -mmin $2 | sed 's/\.\///'`
echo Files:$files
echo ${#files[@]}
for f in $files
do
    echo ! $f
    echo $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/inputs/jobs/$3
    $P3S_HOME/clients/dataset.py -g -i $d -f $f -J $P3S_HOME/inputs/jobs/$3
done
