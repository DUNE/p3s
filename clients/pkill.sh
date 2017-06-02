#!/bin/sh

# A simple script to list pilots on a node,
# meant to be used with pdsh so you get a summary
# of pilots running on a cluster covered by pdsh

plist=`ps aux | grep pilot | grep -v grep | awk '{print $2}'`
echo $plist
for p in $plist;
do
kill -9 $p
done

