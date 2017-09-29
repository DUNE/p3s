#!/bin/bash

# setting up the p3s environment

export P3S_SERVER="http://p3s-web:80/"
export P3S_SITE='lxvm'
export P3S_PILOTS=300
export P3S_PILOT_TO=3000
export P3S_PILOT_MAXRUNTIME=90000
export P3S_VERBOSITY=0
#
export P3S_DIRPATH=/eos/experiment/neutplatform/protodune/np04tier0/p3s
#
export P3S_PILOTLOG=$P3S_DIRPATH/pilotlog
export P3S_JOBLOG=$P3S_DIRPATH/joblog
#
export P3S_CONDOR_OUTPUT=$P3S_DIRPATH/condorOutput
export P3S_CONDOR_ERROR=$P3S_DIRPATH/condorError
export P3S_CONDOR_LOG=$P3S_DIRPATH/condorLog

env | grep P3S

export DQM_DATA_LIFE=1200 # in minutes, e.g. 24 hrs will be 1440

env | grep DQM
