#!/bin/sh

export P3S_SERVER="http://neutdqm:80/"
export P3S_SITE="neutdqm"


# Simple pilot generator to start multiple pilots on a single WN.

# Note this is currently not portable... neutdqm cluster....

# If the site is set then the server address will be provided
# by the environment. Otherwise, one can use the command line, however N.B. -
# quotes must be respected,  \'-S http://serenity.local:80/\'

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
eval $DIR/pilot.py -s $P3S_SITE &
done
