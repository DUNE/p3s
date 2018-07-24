#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}

echo MSG finished larsoft setup

echo XRD: $P3S_XRD_URI

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage in the data
    export INPUT_FILE=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
else
    echo P3S_XRD_URI defined, using xrdcp to stage in the data
    time xrdcp --silent --tpc first $P3S_XRD_URI/$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE .
    s1=`stat --printf="%s"  $P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE`
    s2=`stat --printf="%s" ./$P3S_INPUT_FILE`
    echo sizes after XRDCP $s1 $s2
    if [ $s1 -eq $s1 ];
    then export INPUT_FILE=./$P3S_INPUT_FILE
    else
	echo XRDCP failure, exiting
	exit -3
    fi

fi

lar -c $P3S_FCL_LOCAL $P3S_INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS

ls -l Lifetime_Run1.txt
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
/afs/cern.ch/user/n/np04dqm/public/p3s/p3s/clients/purity.py -f Lifetime_Run1.txt

cat Lifetime_Run1.txt
echo MSG finished uploading purity data

cd ..
echo ls before
ls $P3S_JOB_UUID
echo du before
du $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

exit 0
