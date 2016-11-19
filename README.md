# ProtoDUNE Prompt Processing System (p3s)
## Design Paper
Supporting documents and an outline of the actual design can be found in
the FNAL DocDB 1861 (authorization required for access).

## Intro
The p3s is the computing platform for protoDUNE to support Data Quality Management (DQM).
Its requirements and mode of operation are different from a typical production system in the following:
* there are stringent ETA requirements for processing jobs since for DQM purposes
the results become stale (not actionable) very fast
* only a portion of the data (configurable) needs to be processed
* in any stage of processing a portion of the data unknown apriory can be dropped
in order to optimize throughput
* processing streams are initiated purely automatically in contrast to a managed
production campaign

## Workflow
While workflow in p3s will be simple compared to a typical production system,
it still includes a few steps and can be modeled as a simple DAG. Different stages
in the workflow may need to be dynamically prioritized in order to get deliverables
in a timely mannter

## Location of the input data
The protoDUNE DAQ writes the data to its own "online buffer" from which it is
transferred to CERN EOS (centralized distributed high-performance disk storage).
In order to continue operation in case of a network outage which could make
EOS inaccessible, the system mush be able to optionally feed from the online buffer
without putting too much extra I/O load on it.

## Approach
The near-time nature of prompt processing requires "just-in-time" job submission
and not be subjected to the often unpredictable latencies in batch systems. An
efficient and tried way to achieve this is the pilot-based job submission.

## Contents
* Web service:
** job queues and definitions
** The pilot
** various testing and debugging scripts

## Software dependencies
* Python3
* Django 1.10
* django-tables2
* RDBMS (TBD but most likely PostgreSQL; sqlite used for development puprposes only)
* Apache





