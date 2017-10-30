#!/bin/bash

# setting up the p3s environment

p3s_dirpath=/home/maxim/p3sdata

export P3S_SERVER="http://serenity.local:8000/"
export P3S_SITE='sagebrush'
export P3S_PILOTS=12
export P3S_VERBOSITY=0
export P3S_DIRPATH=$p3s_dirpath
export P3S_PILOTLOG=/tmp/pilotlog
export P3S_JOBLOG=/tmp/joblog
env | grep P3S

export DQM_SERVER="http://serenity.local:8000/"
env | grep DQM
