#!/bin/sh

export P3S_SERVER="http://neutdqm:80/"


# We keep this as a commment since the infomation will actually be provided
# by the server and the pilot pulls is via the "s" optio
# This is for reference, since once again 
# Simple pilot generator to start multiple pilots on a single WN.
# To preserve the command line, use something like \'-S http://serenity.local:80/\'

#export P3S_SITE="neutdqm"

#export P3S_VERBOSITY=2
#export P3S_DIRPATH="/mnt/nas01/users/mxp/p3sdata/"


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
