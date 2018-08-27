#!/bin/sh

source ~anolivie/public/app/crt/setup.sh

if [ -z ${P3S_JOB_UUID+x} ];
then
    echo P3S_JOB_UUID undefined, setting new value:
    export P3S_JOB_UUID=`uuid`
    echo $P3S_JOB_UUID
fi

ofn=`basename CRTOM_${P3S_JOB_UUID}.log`

~anolivie/public/app/crt/binary/bin/onlinePlots ${INPUTFILES} &> ${OUTPUTDIR}/${ofn}

mkdir ${OUTPUTDIR}/${P3S_JOB_UUID}
cp *.root ${OUTPUTDIR}/${P3S_JOB_UUID}/
