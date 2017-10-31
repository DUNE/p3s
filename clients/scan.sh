#!/bin/sh
echo "${P3S_SITE}"
#if [ "${P3S_SITE}" -eq "sagebrush" ]; then
#    echo hi
#fi
#exit 0



if [ ! -d "$1" ]; then
    echo Directory $1 not found, exiting
    exit 0
fi

if [ -z "$2" ]; then
    echo "No time window defined"
    exit 0
fi

# -- source /afs/cern.ch/user/m/mxp/vp3s/bin/activate

export P3S_HOME=/home/maxim/projects/p3s/

cd $1
d=`pwd`
echo Directory: $d
# echo Files:
f=`find . -maxdepth 1 -mindepth 1 -mmin $2 | sed 's/\.\///'`
echo $P3S_HOME/clients/dataset.py -i $d -f $f
