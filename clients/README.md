# p3s clients
## Overview of principal client apps in p3s
The p3s object model contains the following major classes:
* job
* pilot
* dataset
* workflow

The clients carrying similar names have the function of managing
objects which belong to their respective classes wnd which reside on the server:

* job.py
* pilot.py
* dataset.py
* workflow.py

The server API which all of these scripts use is encapsulated in
the module "serverAPI.py" described in one of the sections below.

## Brief summary of the clients' functionality
### job.py

This client is used to:
* create a job (or a number of jobs) on the server. By default standalone jobs
are created, which are not associated with a workflow. This can be done by reading a description of
job(s) contained in a JSON file. An example (with arbitrary names and variables demonstrates
how JSON is used:
`[
    {
        "name":         "p3s_job",
        "timeout":      "100",
        "jobtype":      "type1",
        "payload":      "/home/p3s/my_executable.py",
        "env":          {"P3S":"TRUE","MYVAR":"FALSE"},
        "priority":     "1",
        "state":        "defined"
    }
]`

* adjust job attributes
* delete a job from the server

## pilot.py

Generates a pilot and performs a small number of other functions.
The lifecycle of a pilot is as follows:
* The process starts and then attempts to contact the server in order to register. At the time of writing
handling timeouts is not imeplemented yet, i.e. the pilot will exit in fail condition if there is not
response from the server. This behavior will be improved in future development.

* Upon successful registration, the pilot enters a loop. In each iteration it send a job request
to the server. If the request is not granted, the pilot sleeps for a configurable period of time
and make another attempts. Having exhausted the maximal number of attempts (also configurable), the pilot
exits normally.

* If a matching job is identified by the server, the will receive a message containing the description
of the payload (e.g. the path to the script/wrapper/executable that needs to be run). The pilot then
initiates job execution using the Python "subprocess" machinery.

## workflow.py

Creates and manipulates DAGs and workflows. DAGs serve as templates for actual active workflows.



## Interfaces
### Server interface

* serverAPI.py: translates calls to methods in scripts to HTTP messages sent to the server
utilizing *urllib*. It is used by most all clients.

Please see individual documentation for the clients listed above which is
contained in files named like WORKFLOW.md etc. Same information converted
into PDF (so it's accessible locally and can be printed) can be found in
**p3s/documentation**.


There are additional clients which perform tests or a combination
of procedures on these objects, such as
* injector.py - scans a directory for new files and created workflow with the new data as input
* urltest.py (deprecated) - generic HTTP interface to the server
* verifyImport.py - verifies that dependecies are satisfied, i.e. certain packages can be imported


# Service Scripts
## Pilots
The script pgen.sh serves as a basic generator of pilots, in case multiple pilots need to run
on same node. The number of concurrent pilots is configurable on the command line.

