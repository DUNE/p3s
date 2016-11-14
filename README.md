# ProtoDUNE Prompt Processing System (p3s)
## Intro
The p3s is the computing platform for protoDUNE to support Data Quality Management (DQM).
Its requirements and operation is different from a typical production system in the following:
* there are stringent ETA requirements for processing jobs since for DQM purposes the results become
stale (not actionable) very fast
* only a portion of the data (configurable) needs to be processed
* in any stage of processing a portion of the data unknown apriory can be dropped
in order to optimize throughput

# Other Documentation
An outline of the prompt processing system design is documented in DUNE DocDB 1861.

# Contents
* job queues and definitions
* pilots
* various testing and debugging scripts




