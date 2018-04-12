source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh
source /afs/cern.ch/work/t/tingjun/public/larsoft/localProducts_larsoft_v06_73_00_e15_prof/setup
mrbslp

lar -c beamana_job.fcl $P3S_INPUT_DIR/$P3S_INPUT_FILE -n 1
