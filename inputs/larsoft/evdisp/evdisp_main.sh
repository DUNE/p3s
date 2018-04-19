#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}


if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage the data
    export INPUT_FILE=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
else
    echo P3S_XRD_URI defined, using xrdcp
    time xrdcp --silent --tpc first $P3S_XRD_URI/$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE .
    export INPUT_FILE=./$P3S_INPUT_FILE
fi


lar -c $P3S_FCL_LOCAL $INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS


export DESTINATION=$P3S_DATA/$P3S_EVDISP_DIR/$P3S_JOB_UUID

echo making $DESTINATION
mkdir $DESTINATION

pngs=`ls *.png`

ls -l *.png

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage out the data
    for f in $pngs
    do
	[ -s $f ] && cp $f $DESTINATION
    done
else
    echo P3S_XRD_URI defined, using xrdcp
    time xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION
fi


cd ..
echo ls before
ls $P3S_JOB_UUID
echo du before
du $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID
echo ls after
ls $P3S_JOB_UUID
echo '-----------------'

exit 0
