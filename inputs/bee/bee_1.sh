#!/bin/bash

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export BEE_HOME=${P3S_HOME}/tools/live3d-to-bee/


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

############################################################
############################################################
# LARSOFT HERE
############################################################
############################################################

unset PYTHONPATH # just in case
echo MSG initializing virtual environment
source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate
echo MSG check Python: `python -V`
echo ---
echo MSG check PYTHONPATH: $PYTHONPATH
echo ---

echo MSG finished python setup


export DESTINATION=$P3S_DATA/$P3S_BEE_DIR/$P3S_JOB_UUID

echo making $DESTINATION
mkdir $DESTINATION
if [ ! -d "$DESTINATION" ]; then
    echo Directory $DESTINATION was not created, exiting
    $P3S_HOME/clients/service.py -n monitor -m "Failed to create $DESTINATION"
    exit -1
fi


cp $BEE_HOME/* .
root -b -q loadClasses.C

BEE_INPUT=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
BEE_OUTPUT=`echo $P3S_INPUT_FILE | sed s/root/json/`
root -b -q loadClasses.C 'run.C("'$BEE_INPUT'", "'$BEE_OUTPUT'")'


#
jsons=`ls *.json` 

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage out the data
    for f in $jsons
    do
	[ -s $f ] && cp $f $DESTINATION
    done
else
    echo P3S_XRD_URI defined, using xrdcp to stage out the data
    for f in $jsons
    do
	[ -s $f ] && time xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION
    done
fi

echo MSG finished copying JSON files

cd ..
echo ls before
ls $P3S_JOB_UUID
echo du before
du $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

echo 'done with cleanup'
