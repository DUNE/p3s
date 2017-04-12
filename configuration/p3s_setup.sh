#!/bin/bash

# setting up the p3s environment

# Default server/site:
p3s_server="serenity.local"
p3s_site="sagebrush"
p3s_dirpath="/home/maxim/p3sdata/"
# override for neutdqm:

h=`hostname`

echo Setting up environment on host $h
if [[ $h == neutdq* ]];
then
    p3s_server="neutdqm"
    p3s_site="neutdqm"
    p3s_dirpath="/mnt/nas01/users/mxp/p3sdata/"
fi 

port=8000

if [ -z "$1" ]
  then
      echo "Using default server" $p3s_server
else
    p3s_server=$1
fi

if [ -z "$2" ]
  then
      echo "Using default port" $port
else
    port=$2
fi



export P3S_SERVER="http://$p3s_server:$port/"
export P3S_SITE=$p3s_site

export P3S_VERBOSITY=2
export P3S_DIRPATH=$p3s_dirpath

env | grep P3S
