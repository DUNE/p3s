#!/bin/bash

# setting up the p3s environment

p3s_dirpath=/eos/experiment/neutplatform/protodune/np04tier0/p3s

export P3S_SERVER="http://p3s-web:80/"
export P3S_SITE='lxvm'
export P3S_PILOTS=300
export P3S_PILOT_TO=3000
export P3S_VERBOSITY=0
export P3S_DIRPATH=$p3s_dirpath
export P3S_PILOTLOG=$P3S_DIRPATH/pilotlog
export P3S_JOBLOG=$P3S_DIRPATH/joblog
env | grep P3S
