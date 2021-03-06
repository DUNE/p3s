# just a collection of trivial shell code
# to help set up a few sites. No longer used for real work.

#!/bin/bash

# setting up the p3s environment

# Default server/site:
p3s_server="serenity.local"
p3s_site="sagebrush"
p3s_dirpath="/home/maxim/p3sdata/"
# override for neutdqm:

h=`hostname`
port=80

echo Setting up environment on host $h
if [[ $h == neutdq* ]];
then
    p3s_server="neutdqm"
    p3s_site="neutdqm"
    p3s_dirpath="/mnt/nas01/users/mxp/p3sdata/"
    port=80
fi 

# FIXME - below will work for testing on lxplus
# but hostname will be different on lxbatch, caveat emptor
if [[ $h == lx* ]];
then
    p3s_server="p3s-web"
    p3s_site="lxvm"
    p3s_dirpath=""
    port=8000
fi 


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
