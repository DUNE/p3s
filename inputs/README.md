# p3s "inputs"
## Overview
The directory **p3s/inputs** contains two types of material:
* a few simple examples which are useful for testing and debugging
* realistic templates for running DQM payloads for protoDUNE

The three main file types to be found here are
* JSON
* XML
* Bash shell scripts

The former containes a _list_ of jobs in JSON format, although
in most examples there is only one item on that list. Any number
of jobs can reside within a file and they can be send to the
server for execution using the _job.py_ client.

The XML source files (which typically have the .graphml extension)
are expected to contain DAG descriptions (workflow templates)
in _GraphML_ format. The reason this format was chosen to represent
DAGs is that it is compatible with a number of third-party tools
which are useful for parsing and visualization.

## The "jobs" directory
p3s supports both workflows (collections of related jobs) as well
as jobs not included in any workflow. Such jobs can be injected
into the system using specially formatted job descriptions similar
to those present in this directory.

The files named like "job_template*" are meant to be used with the
like job.py client in the "clients" folder. Example:

`
job.py -j mytemplates.json
`
The client interacts with the p3s server and creates a database
entry (or entries) correponsing to the content of the template file.
A single file may contain a description of a single job, or multiple jobs:
the template file is expected to be formatted as a JSON list.


## larsoft
These files are application-specific and are meant to support LArSoft-based
applications running at CERN and elsewhere

## Workflows and DAGs: an overview

A DAG defined by the user is expected to serve as a template for
actual instances of workflows. DAGs can be stored in a few formats.
Most of the time p3s utilizes the GraphML schema (format)
which is fairly standard and can be parsed by the Networkx package
as well as a number of other editors and network-oriented packages.

By default edges and nodes in a workflow inherit properties of the DAG the workflow
is derived from. The _workflow.py_ client provides a possibility to
overwrite values in the template by supplying a JSON string or
a JSON file in the format
`
{"my":{"foo":"bar"}}
`
where "my" is the name of the object (node or edge in which case it
will look like "source:target" with actual names of the source and target"),
and the dictionary within lists the attributes to
be defined when the client is run (such as "workflow.py").

## Workflow Examples

### 1filter
A simple example of a DAG containing just one payload job, with additional
"NOOP" nodes provided as entry and exit points

### 3filters
Similar to the above, but with three filters working on same data
in parallel

### chain
Contains examples of chained jobs
