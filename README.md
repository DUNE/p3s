# ProtoDUNE Prompt Processing System (p3s)
## About this document
This document is available on the p3s page on GitHub as README.md,
and it also exists as USERMANUAL.pdf in the *documents* directory
to make its meaning clear. It's purpose it to guide beginning and
prospective users in installing and trying out p3s, which is currently
under development. Pardon the dust.

## Software dependencies
The system consists of the server and client components. Their
software de[endencies (which overlap) are listed below. They
obviously must be installed before the code can run.

### p3s server dependencies

* Python3.5

* Django 1.10+

* django-tables2

* RDBMS (TBD but most likely PostgreSQL; sqlite used for development puprposes only)

* Apache 2.4

* NetworkX

### p3s client dependencies

* Python3.5

* Django 1.10+ (to include full timezone functionality)

* NetworkX

### Known issues

* NetworkX: some versions may present compatibility issues, resolving this is reponsibility of the developer

* Apache 2.4 deployment may differ on different flavors of Linux, this needs to be addressed during deployment


## Installation
### Getting the software
At the time of writing, the simplest way to get the code
is by cloning the repo https://github.com/DUNE/p3s.git

Please DO NOT COMMIT/PUSH ANYTHING TO THIS REPO unless
you contact the developer (M.Potekhin). Effort will be
made to package the code for a more robust installation
method.

### Contents of the installation
p3s installation tree contains the following directories
which are necessary for its function:

* **promptproc** - the workflow managment and monitoring server

* **clients** - an assortment of clients for creation and manipulation of the objects residing in the server, mostly tailored to support a specific class.

Other directories not critical for the system functionality:

* **inputs** contains files that can be used as examples
and/or templates for initial testing of p3s but which are not meant to be
a part of a useful application or production type of environment.

* **documents** (obviously)

* **sandbox** - which stored arbitrary snippets of code of interest
only to the developers and which won't be helpful for testers
or users.


## Initializing the Database

Coming from the source code distirbution, the p3s server will utilize the sqlite database
which comes with Django. Production application may need a more powerful RDBMS such as PostgreSQL
but this is beyond the scope of this document.

The sqlite DB is not initialized to work with the p3s server when you first get hold of the code.
This needs to be done as follows:

* change directory to p3s/promproc

* run

   * ./manage.py makemigrations
   * ./manage.py migrate


## Define at least one data type

Meaningful testing requires that at least one datatype is defined
in the system which should match whatever datatype(s) you use
in your workflow template (DAG).

In the examples which come with the code the ".txt" extension is often used
to demonstrate basic functionality. The system needs it to be able to autogenerate
file names if necessary.

If your files all have extension
'.txt' you may define the datatype "TXT" (which again must
be consistent with you DAG) and use the following command
to add the datatype to the server:

./dataset.py -R -j '{"name":"TXT", "ext":".txt", "comment":"testing text files"}'

If you no longer need the datatype you created (perhaps as the result
of testing), it can be removed from the server as folllows:

./dataset.py -D test


## Running the development server

Using the development server should only be done in testing/educational scenarios.
It is recommende that you use the single-threaded mode of operation and use
the following command to start the server:

./manage.py runserver --nothreading

which again is done from the directory p3s/promprproc

This will default to the port 8000 and the server will be visible at the address
localhost:8000 (plus maybe some bits of URLs depending on the version).

If you use ssh to connect the machine which runs the server, you could use ssh
tunneling to get access to this host and port combination.



## Embedded documentation
Many directories contain .md files that are easy to read in the browser
on GitHub by just clicking on a file. Some of the more important instructions
are converted to PDF format and kept in the "documentation" folder in this
repo.

If you want to convert any of the .md files to PDF at will, the following
utility may be used which is easy to install on Linux - see this example:

pandoc -s -o README.pdf README.md

## Learning about the clients
All clients have the '-h' or the equivalent '--help' option which summarizes
the command line syntax, in addition some have the 'usage' option which may
provide more info.

## Design Paper and Motivation
Supporting documents and an outline of the design can be found in
the FNAL DocDB 1861 (authorization required for access).

The p3s is the computing platform for protoDUNE to support Data Quality Management (DQM).
Its requirements and mode of operation are different from a typical production system
in the following:
* there are stringent ETA requirements for processing jobs since for DQM purposes
the results become stale (not actionable) very fast
* only a portion of the data (configurable) needs to be processed
* in any stage of processing a portion of the data unknown apriory can be dropped
in order to optimize throughput
* there is no retry mechanism since any substantial delay in processing a unit
of data makes the result less relevant (again, the focus is on ETA)
* processing streams are initiated purely automatically and in real time
by the data arriving from DAQ
* there is no distinct data handling system for two reasons. First, the cluster
which runs p3s is either literally local or can access data through a POSIX-like
interface with some modest development and deployment effort. Second, a data
handling system would introduce additional complexity, latency and potentially
failure modes. Instead, p3s relies on federated storage such as provided by an
instance of XRootD. A high-performance NAS could be an alternative. In either case,
for purposes of access and processing the data is essentially local on the cluster.

## Job dispatch
### Pilots
To minimize latency and provide the ability to run transparently on
a few local resources (e.g. the cluster at EHN1, CERN Tier-0 and perhaps
some other facilities on or around CERN campus) any reliance on the flavor
of the underlying batch system needs to be eliminated. In addition,
latencies inherent in any batch system should be optimally mitigated. Both
problems are addressed by utilizing a pilot-based job dispatch, where
the pilots (agents) contact a central service and only receive jobs in
case the batch slot is secured and the environment validated. This also
combats a few failure modes.


A workflow is instantiated based on a DAG template. DAG templates are persistent
in the database and can be added or deleted at will. A convenient external
representation of a DAG is a XML file describing the corresponding graph,
which can be readily parsed and used for both import and export of DAGs.

### XML Schema
At the time of writing, the GraphML schema is used as the "input language"
describing graphs. It's one of standard schemas for describing graphs
and editors and other tools exist for manipulating data in this format,
altough it's human readable and can be easily edited by hand

### Pairing Jobs to Data
Setting the environment variables to supply information about I/O
is preferred due to flexibility of such method. Dependencies between
interfaces of jobs in a workflow need to be minimized.

Once a WF is defined (based on a DAG), so are dataset characteristics
(i.e. file names) in each edge of the graph. At this point the environment
of each node can be updated to include references to file, via
environment variables.


## Components
* Web service:

   * workflows and their templates (dags)
   
   * jobs
   
   * data
   
   * handling of pilots' requests for registration and payload
   
* Clients

   * The *pilot* - submission and management of pilot data on the server
   
   * The *job* - submission of job definitions to the server and management of job data on the server
   
