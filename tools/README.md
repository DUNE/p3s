# TOOLS

This directory contains an assortment of useful scripts etc to help develop and debug p3s.
The "scripts" folder is for basic scripts that may be useful for debugging some of the
p3s interfaces. The rest of the folder contains emulation tools which provide mock up data
to test p3s workflows.

To build the executable for the pedestal emulator, the following command may be used:
```
root_compile.sh pedestal_emulator
```

The resulting ./pedestal_emulator.exe takes the following arguments

* the name of the ROOT file where the histograms will be stored
* statistics (entries in the histogram)
* number of TPC channels

The "accumulator" application is used to

* initialize a histogram file with a configurable number of TPC channels
* use the "add" operation to accumulated statisics from any number of files,
although only one is open at a time so it needs to be run requisite number of times

