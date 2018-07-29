#!/bin/bash

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export BEE_HOME=${P3S_HOME}/tools/live3d-to-bee/

cp $BEE_HOME/* .
root -b -q loadClasses.C

BEE_INPUT=$P3S_DATA/$P3S_INPUT_DIR/$P3S_INPUT_FILE
root -b -q loadClasses.C 'run.C("'$BEE_INPUT'", "test.json")'
