#!/bin/bash

# setting up the p3s environment

# 1. Python virtual env and P3S home
export P3S_VENV='/afs/cern.ch/user/n/np04dqm/public/vp3s'
export P3S_HOME='/afs/cern.ch/user/n/np04dqm/public/p3s/p3s'

# 2. Service-related parameters
export P3S_SERVER="http://p3s-web:80/"
export P3S_SITE='lxvm'
export P3S_PILOTS=100 # 00
export P3S_PILOT_TO=1000
export P3S_PILOT_MAXRUNTIME=90000
export P3S_VERBOSITY=0

# 3. Local Condor directories
export P3S_CONDOR_BASE=/afs/cern.ch/work/n/np04dqm/condor
export P3S_CONDOR_OUTPUT=$P3S_CONDOR_BASE
export P3S_CONDOR_ERROR=$P3S_CONDOR_BASE
export P3S_CONDOR_LOG=$P3S_CONDOR_BASE


# 4. Data location
export P3S_DIRPATH=/eos/experiment/neutplatform/protodune/np04tier0/p3s

# 5. P3S logs
export P3S_PILOTLOG=$P3S_DIRPATH/pilotlog
export P3S_JOBLOG=$P3S_DIRPATH/joblog


env | grep P3S

# 6. DQM
export DQM_DATA_LIFE=1200 # in minutes, e.g. 24 hrs will be 1440
export DQM_SERVER="http://p3s-content:80/"

env | grep DQM

# Set DISPLAY to a dummy value so that ROOT does not print warnings at CERN.

export DISPLAY="0:0"
