#!/bin/sh

# Simple pilot generator to start multiple pilots on a single WN
N=1
if [ -n "$1" ];
then
    if [ "$1" -eq "$1" ] 2>/dev/null; then
	N=$1
    fi
fi


for i in `seq 1 $N`;
do
    eval $PWD/pilot.py $2
done
