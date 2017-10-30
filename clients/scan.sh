#!/bin/sh

if [ ! -d "$1" ]; then
    echo Directory $1 not found, exiting
    exit 0
fi

if [ -z "$2" ]; then
    echo "No time window defined"
    exit 0
fi

# -- source /afs/cern.ch/user/m/mxp/vp3s/bin/activate

export $P3S_HOME=/home/maxim/projects/p3s/

$p=`$P3S_HOME/clients/summary.py -p`

cd $1
d=`pwd`
echo Directory: $d
echo Files:
find . -maxdepth 1 -mindepth 1 -mmin $2 | sed 's/\.\///'
