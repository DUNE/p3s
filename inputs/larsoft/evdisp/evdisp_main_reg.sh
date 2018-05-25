#!/bin/bash

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

source $P3S_HOME/configuration/lxvm_np04dqm.sh > /dev/null
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate


if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}

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


export DESTINATION=$P3S_DATA/$P3S_EVDISP_DIR/$P3S_JOB_UUID

echo making $DESTINATION
mkdir $DESTINATION
if [ ! -d "$DESTINATION" ]; then
    echo Directory $DESTINATION was not created, exiting
    $P3S_HOME/clients/service.py -n evdisp -m "Failed to create $DESTINATION"
    exit -1
fi

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
    echo P3S_XRD_URI defined, using xrdcp to stage out the data
    for f in $pngs
    do
	[ -s $f ] && time xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION
    done
fi

$P3S_HOME/clients/evdisp.py -a

echo 'done reg'

cd ..
echo ls before
ls $P3S_JOB_UUID
echo du before
du $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

echo 'done'
exit 0
