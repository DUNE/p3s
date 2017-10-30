#!/bin/sh

# Simple pilot generator to start multiple pilots on a single WN.
# To preserve the command line, use something like \'-S http://serenity.local:80/\'

DIR=`dirname "$(readlink -f "$0")"`
N=1
if [ -n "$1" ];
then
    if [ "$1" -eq "$1" ] 2>/dev/null; then
	N=$1
    fi
fi

line=''
for i in `seq 1 $N`;
do
#    line="$DIR/pilot.py $2 &" $line
eval $DIR/pilot.py $2 &
done
