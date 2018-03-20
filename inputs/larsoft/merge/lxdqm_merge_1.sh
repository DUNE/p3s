#!/bin/sh

export P3S_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/p3s
export DQM_HOME=/afs/cern.ch/user/n/np04dqm/public/p3s/dqmconfig

source $P3S_HOME/configuration/lxvm_np04dqm.sh > /dev/null

source /afs/cern.ch/user/n/np04dqm/public/vp3s/bin/activate

export P3S_INPUT_DIR=$P3S_DIRPATH/input

if [ ! -d "$P3S_INPUT_DIR" ]; then
    $P3S_HOME/clients/service.py -n merge -m "Problem with directory $P3S_INPUT_DIR"
    exit 1
fi

env | grep P3
cd $P3S_INPUT_DIR
d=`pwd`
echo Directory: $d
files=`find . -maxdepth 1 -mindepth 1 -mmin $1 -size +1 -name "moo*" | sed 's/\.\///'`
echo $files
for f in $files
do
    echo ! $f

    $P3S_HOME/p3s/tools/accumulator.exe add foo.root $f
done
