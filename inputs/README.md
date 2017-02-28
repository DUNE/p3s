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
The files named like "job_template*" are meant to be used with the
like job.py client in the "clients" folder. Example:

`
job.py -j mytemplates.json
`

The client interacts
with the p3s server and creates a database entry correponsing to the
content of the job template file. A single file may contain
a description of a single job, or multiple jobs:
the template file is expected to be formatted
as a JSON list.


## Workflows and DAGs
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

