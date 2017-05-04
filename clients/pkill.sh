#!/bin/sh

# Simple pilot eliminator, meant to be used with pdsh

plist=`ps aux | grep pilot | grep -v grep | awk '{print $2}'`
echo $plist
for p in $plist;
do
kill -9 $p
done

