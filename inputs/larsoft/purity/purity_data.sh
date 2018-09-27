#!/bin/bash

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


echo MSG Will perform larsoft setup
date
source ${P3S_LAR_SETUP}

retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error: larsoft not found"
    exit $retVal
fi

date
echo MSG finished larsoft setup with job uuid: $P3S_JOB_UUID

echo XRD: $P3S_XRD_URI

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage in the data
    export INPUT_FILE=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
else
    echo P3S_XRD_URI defined, using xrdcp to stage in the data
    time (xrdcp --silent --tpc first $P3S_XRD_URI/$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE .) 2>&1
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

P3S_OUTPUT_FILE=`echo $P3S_INPUT_FILE | sed 's/raw/mon/'`


echo Output file: $P3S_OUTPUT_FILE
echo Job ID: $P3S_JOB_UUID

# ---
echo MSG starting larsoft
date
lar -c $P3S_FCL_LOCAL $INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS 2>&1
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Error: larsoft abnormal termination"
    exit $retVal
fi
date
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



roots=$P3S_OUTPUT_FILE # can't do`ls *.root` since it will include the input file
jsons=`ls *.json`
pngs=`ls *.png`
txts=`ls *.txt`

if [ -z ${P3S_XRD_URI+x} ];
then
    echo P3S_XRD_URI undefined, using FUSE to stage out the data
    for f in $roots $jsons $pngs $txts
    do
	[ -s $f ] && cp $f $DESTINATION
    done
else
    echo P3S_XRD_URI defined, using xrdcp to stage out the data
    for f in $roots $jsons $pngs $txts
    do
	[ -s $f ] && time (xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION) 2>&1
    done
fi

echo MSG finished copying root,json,png,txt files

cd ..
#echo ls before: $P3S_JOB_UUID
#ls $P3S_JOB_UUID
#echo du before
du -sh $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

echo MSG done with cleanup
# ---
cd $DESTINATION

echo Looking at JSON
ls -l *.json
summary=`ls *summary.json`
echo MSG found the run summary $summary

f=`ls -m *FileList.json`
descriptors=`echo $f | tr -d ' '`
ld=`echo -n $descriptors | wc -m`
if [ $ld == 0 ]; then
    echo No descriptots found
    exit 3
fi


# FIXME: uncomment when Justin fixes the app

#echo MSG Found the file descriptors: $descriptors
#$P3S_HOME/clients/monrun.py -s $summary -d $descriptors -j monitor
#echo MSG finished registration

export lfile=`ls Lifetime*.txt`

# we can either parse the file name, or use the recently available run info from TXT
#export run=`echo $lfile | tr -d 'Lifetime_Run' | tr -d '.txt'`

$P3S_HOME/clients/purity.py -f $lfile # -r $run

exit 0


# echo $INPUT_FILE | mail -s $P3S_JOB_UUID potekhin@bnl.gov
