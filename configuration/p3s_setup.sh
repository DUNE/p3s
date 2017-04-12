#!/bin/sh

# setting up the p3s environment

# Default server/site:
p3s_server="serenity.local"
p3s_site="sagebrush"

# override for neutdqm:

h=`hostname`

echo Setting up environment on host $h

[[ $h == neutdq* ]] && (p3s_server="neutdqm"; p3s_site="neutdqm")

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
export P3S_DIRPATH=/home/maxim/p3sdata/ # example: for cases where I/O is in one directory

env | grep P3S
