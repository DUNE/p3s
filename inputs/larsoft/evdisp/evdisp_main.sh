#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}


if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE
    export INPUT_FILE=$P3S_INPUT_DIR/$P3S_INPUT_FILE
else
    echo P3S_XRD_URI defined, using xrdcp
    time xrdcp --silent --tpc first $P3S_XRD_URI/input/$P3S_INPUT_FILE .
    export INPUT_FILE=./$P3S_INPUT_FILE
fi


lar -c $P3S_FCL_LOCAL $INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS


dest=$P3S_EVDISP_DIR/$P3S_JOB_UUID

echo making $dest
mkdir $dest

pngs=`ls *.png`

ls -l *.png

for f in $pngs
do
    [ -s $f ] && cp $f $dest
done

if [ ! -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI defined, clean up all files
    echo ls before
    ls
    echo du before
    du .
    echo '-----------------'
    rm ./*
    echo ls after
    ls
    echo du after
    du .
    echo '-----------------'
fi


exit 0
