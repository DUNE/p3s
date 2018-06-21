#!/bin/bash

echo pid, ppid: $$ $PPID

if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo No input file specified, entering sleep mode
    /bin/sleep 1
    exit
fi


echo Using input file $P3S_INPUT_FILE

f=`wc -l $P3S_INPUT_FILE`
d=`date`
echo $d $f >> $P3S_OUTPUT_FILE
