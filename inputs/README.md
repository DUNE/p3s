# p3s "inputs"

## Overview

The directory **p3s/inputs** contains templates
and code samples which describe a few types of p3s
objects, for example:

* jobs descriptions to be sent to p3s
* workflows
* _data types_ and data
* p3s sites

These pieces of information are meant to be used
with appropriate p3s clients e.g. job descriptions in
JSON format are read and processed by the "job" client,
workflow descriptions are processed by the "workflow" client etc.
Each client performs parsing and interacts with the p3s
server to communicate the user's request.

In general there are two types of material in this folder:
* a few very simple examples which are useful for testing and debugging
* realistic templates for running DQM payloads for protoDUNE

The three main file types to be found here are
* JSON
* XML
* Bash shell scripts

Details on these types are provided below.


## JSON (and the corresponding "jobs" directory)

p3s supports both workflows (collections of related jobs) as well
as individual jobs not included in any workflow. Such jobs can be injected
into the system using JSON-formatted _job descriptions_ similar
to those present in the **jobs** directory.

Such files are meant to be used with the
_job.py_ client in the "clients" folder. Example:

`
p3s/clients/job.py -j myJob.json
`

The client then interacts with the p3s server and creates a database
entry (or entries) corresponding to the content of the JSON file.
A single file may contain a description of a single job, or multiple jobs.
Either way,  the file is expected to be formatted as a _JSON list_.

Any number of job descriptions can reside within a file (including a single job)
and they can be send to the server for execution using the _job.py_ client.


## XML (GraphML schema)

### The client
The main consumer of these files is the _workflow.py_ client of p3s.

### DAG templates formatted in GraphML

The XML source files (which typically have the .graphml extension
but that's not critical)
are expected to contain DAG descriptions (workflow templates)
in _GraphML_ format. The reason this format was chosen to represent
DAGs is that it is compatible with a number of third-party tools
which are useful for parsing and visualization.

### Workflows vs DAGs

A DAG defined by the user is expected to serve as a _template_ for
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

### Workflow Examples

#### 1filter
A simple example of a DAG containing just one payload job, with additional
"NOOP" nodes provided as entry and exit points

#### 3filters
Similar to the above, but with three filters working on same data
in parallel

#### chain
Contains examples of chained jobs

## The "larsoft" directory

These files are application-specific and are meant to support LArSoft-based
applications running at CERN and elsewhere. It contains subdirectories

* **test** for general testing of larsoft
* **crt** for Cosmic Rate Tagger software
* **evdisp** for the Event Display


