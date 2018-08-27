# CRT DQM Jobs that Run Through LArSoft
## Developer's notes
Once the CRT has been integrated into the TPC data stream, all
data processing will be handled by ART jobs.  The wrappers in 
this directory will run LArSoft jobs to produce .root files 
that contain TObjects, usually TH1s, to be drawn to PNG files. 

## Output data location
It may be preferable to keep the outputs according to same convention
as the rest of the current DQM jobs, i.e. under monitor/uuid. For that
reaso, the wrapper should be updated --mxp--
