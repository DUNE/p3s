# ProtoDUNE Prompt Processing System (p3s)
## Intro
The p3s is the computing platform for protoDUNE to support Data Quality Management (DQM).
Its requirements and operation is different from a typical production system in the following:
* there are stringent ETA requirements for processing jobs since for DQM purposes
the results become
stale (not actionable) very fast
* only a portion of the data (configurable) needs to be processed
* in any stage of processing a portion of the data unknown apriory can be dropped
in order to optimize throughput

## Workflow
While workflow in p3s will be simple compared to a typical production system,
it still includes a few steps and can be modeled as a simple DAQ. Different stages
in the workflow may need to be dynamically prioritized in order to get deliverables
in a timely mannter

## Other Documentation
An outline of the prompt processing system design is documented in DUNE DocDB 1861.

## Approach
The near-time nature of prompt processing requires "just-in-time" job submission
and not be subjected to the often unpredictable latencies in batch systems. An
efficient and tried way to achieve this is the pilot-based job submission.

# Contents
* Web service:
** job queues and definitions
* The pilot
* various testing and debugging scripts




