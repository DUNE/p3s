#!/bin/sh
export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


# echo MSG Will perform larsoft setup
# date
# source ${P3S_LAR_SETUP}

# retVal=$?
# if [ $retVal -ne 0 ]; then
#     echo "Error: larsoft not found"
#     exit $retVal
# fi

source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
setup dunetpc ${DUNETPCVER} -q ${DUNETPCQUAL}
setup cmake v3_10_1

date
echo MSG finished larsoft setup with job uuid: $P3S_JOB_UUID

setup cmake v3_10_1
echo MSG set up cmake

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

# localize the output to make it easier to clean up later.

tmpdir=$P3S_JOB_UUID
mkdir $tmpdir
cd $tmpdir
echo Created a working directory:
pwd


/afs/cern.ch/user/a/anolivie/public/app/crt/binary/bin/onlinePlots ${P3S_INPUT_FILE}
echo MSG crt binary completed

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

roots=$P3S_OUTPUT_FILE    #`ls *.root`

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
	[ -s $f ] && time (xrdcp --silent --tpc first $f $P3S_XRD_URI/$DESTINATION) 2>&1
    done
fi

echo MSG finished copying root files
cd ..
#echo ls before: $P3S_JOB_UUID
#ls $P3S_JOB_UUID
#echo du before
#du -sh $P3S_JOB_UUID
echo '-----------------'
rm -fr $P3S_JOB_UUID

echo MSG done with cleanup

cd $DESTINATION
cp $ROOT_MACRO_LOCATION/$ROOT_MACRO_NAME .

echo MSG Startng the ROOT macro
date
time ROOT_MACRO_TORUN=${ROOT_MACRO_NAME}'("'${P3S_OUTPUT_FILE}'");'
time root -b -l -q $ROOT_MACRO_TORUN  >& ${P3S_INPUT_FILE}.log
date
echo Finished the ROOT macro, looking at JSON
ls -l *.json

summary=`ls run*summary.json`
echo MSG found the run summary $summary

f=`ls -m *FileList.json`
descriptors=`echo $f | tr -d ' '`
ld=`echo -n $descriptors | wc -m`
if [ $ld == 0 ]; then
    echo No descriptots found
    exit 3
fi


echo MSG Found the file descriptors: $descriptors

$P3S_HOME/clients/monrun.py -s $summary -d $descriptors -j monitor

echo MSG finished registration
date | mail -s $P3S_JOB_UUID potekhin@bnl.gov
exit 0
