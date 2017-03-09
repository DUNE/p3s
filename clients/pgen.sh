#!/bin/sh

# Simple pilot generator to start multiple pilots on a single WN
DIR=`dirname "$(readlink -f "$0")"`
N=1
if [ -n "$1" ];
then
    if [ "$1" -eq "$1" ] 2>/dev/null; then
	N=$1
    fi
fi


for i in `seq 1 $N`;
do
    eval $DIR/pilot.py $2
done
