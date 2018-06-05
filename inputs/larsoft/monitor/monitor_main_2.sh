#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}

echo MSG finished larsoft setup

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage in the data
    export INPUT_FILE=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
else
    echo P3S_XRD_URI defined, using xrdcp to stage in the data
    time xrdcp --silent --tpc first $P3S_XRD_URI/$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE .
    export INPUT_FILE=./$P3S_INPUT_FILE
fi


lar -c $P3S_FCL_LOCAL $INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS

echo MSG larsoft completed
unset PYTHONPATH # just in case
echo MSG initializing virtual environment
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
echo MSG check Python: `python -V`
echo ---
echo MSG check PYTHONPATH: $PYTHONPATH
echo ---

echo MSG finished python setup


export DESTINATION=$P3S_DATA/$P3S_MONITOR_DIR/$P3S_JOB_UUID

echo making $DESTINATION
mkdir $DESTINATION
if [ ! -d "$DESTINATION" ]; then
    echo Directory $DESTINATION was not created, exiting
    $P3S_HOME/clients/service.py -n monitor -m "Failed to create $DESTINATION"
    exit -1
fi

roots=`ls *.root`

ls -l *.root



if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage out the data
    for f in $roots
    do
	[ -s $f ] && cp $f $DESTINATION
    done
else
    echo P3S_XRD_URI defined, using xrdcp to stage out the data
    for f in $roots
    do
	[ -s $f ] && time xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION
    done
fi

echo MSG finished copying root files

cd ..
echo ls before
ls $P3S_JOB_UUID
echo du before
du $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

echo 'done'
exit 0
