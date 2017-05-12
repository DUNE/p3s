#!/bin/sh

# Simple pilot eliminator, meant to be used with pdsh

plen=`ps aux | grep pilot | grep -v grep | wc -l`
echo $plen

