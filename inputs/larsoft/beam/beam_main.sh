source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
echo Finished DUNE setup
source /afs/cern.ch/work/t/tingjun/public/larsoft/localProducts_larsoft_v06_73_00_e15_prof/setup

echo Will do mrbslp
mrbslp

echo dir: $P3S_INPUT_DIR
echo file: $P3S_INPUT_FILE

lar -c beamana_job.fcl $P3S_INPUT_DIR/$P3S_INPUT_FILE -n 1
