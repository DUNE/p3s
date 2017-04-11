# p3s "inputs"
##Overview
This directory contains a few examples which are useful
for testing and debugging. Its subdirectories
contain a number of XML source files (which typically have the .graphml extension).
These XML files are expected to contain
DAG descriptions (workflow templates) in the GraphML formate.

There are also a number of JSON-formatted files contain
additional information necessary to form a functional workflow
from the DAG template. The following information can be provided
my means of these JSON files:
* job description(s) - paths to payload jobs
* additional file (data) parameters for a workflow
* additional job parameters for a workflow

##The "jobs" directory
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


## Workflows and DAGs: an overview
A DAG is supposed to serve as a template for an instance
of workflow. DAGs can be stored in a few formats.
Most of the time p3s utilizes the GraphML schema (format)
which is fairly standard and can be parsed by the Networkx package
as well as a number of other editors and network-oriented packages.

By default edges and nodes in a workflow inherit properties of the DAG the workflow
is derived from, but they can also be overwritten by supplying a JSON string or
a JSON file in the format
`
{"my":{"foo":"bar"}}
`
where "my" is the name of the object (node or edge in which case it
will look like "source:target" with actual names of the source and target"),
and the dictionary within lists the attributes to
be defined when the client is run (such as "workflow.py").

##Workflow Examples

###1filter
A simple example of a DAG containing just one payload job, with additional
"NOOP" nodes provided as entry and exit points

###3filters
Similar to the above, but with three filters working on same data
in parallel

###chain
Contains examples of chained jobs
