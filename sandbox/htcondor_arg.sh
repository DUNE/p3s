#!/bin/sh
if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit
else
    echo arg!
    ls $1
fi

