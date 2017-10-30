#!/bin/bash

echo pid, ppid: $$ $PPID

if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo No input file specified, entering sleep mode
    /bin/sleep 10
    exit
fi


echo Using input file $P3S_INPUT_FILE

wc -l $P3S_INPUT_DIR/$P3S_INPUT_FILE > $P3S_OUTPUT_FILE
