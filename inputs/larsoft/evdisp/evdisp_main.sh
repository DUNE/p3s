#!/bin/bash

if [ -z ${P3S_LAR_SETUP+x} ];
then
    echo P3S_LAR_SETUP undefined, exiting
    exit
fi


source ${P3S_LAR_SETUP}

lar -c $P3S_FCL_LOCAL $P3S_INPUT_DIR/$P3S_INPUT_FILE -T $P3S_OUTPUT_FILE -n$P3S_NEVENTS

dest=$P3S_EVDISP_DIR/$P3S_JOB_UUID

echo making $dest
mkdir $dest

pngs=`ls *.png`

for f in $pngs
do
    [ -s $f ] && cp $f $dest
done

exit
