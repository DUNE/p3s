# LArSoft Job definitions and templates
## About
This folder contained application-specific job configuration files
meant to be run within the framework of the protoDUNE Data Quality
Monitoring system, with p3s being the main engine.

There are three clients in p3s which can use the JSON files describing
jobs:

- **testwrapper**
- **job**
- **dataset**

A job description usually contains a reference to the file name
used as input. Command line options for these clients provide
a possibility to override the input file name from the command line,
therefor reducing the need to continuously edit JSON and also making
possible automation when jobs need to be defined programmatically.

## Payloads

- **purity**
- **event display**
- **monitor**
