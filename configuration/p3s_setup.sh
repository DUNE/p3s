#!/bin/sh

# setting up the p3s environment

p3s_server="serenity.local"
port=8000

if [ -z "$1" ]
  then
      echo "Using default server"
else
    p3s_server=$1
fi

if [ -z "$2" ]
  then
      echo "Using default port"
else
    port=$2
fi

echo setting $p3s_server on port $port

export P3S_SERVER="http://$p3s_server:$port/"
export P3S_VERBOSITY=2
export P3S_DIRPATH=/home/maxim/p3sdata/ # example: for cases where I/O is in one directory
