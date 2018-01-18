Created by: Maxim Potekhin

January 2018

Version 1.00

---

# About this document
This paper provides a broad overview of the system
that may be of interest to developers and shifters.
It does not contain "how-to" information which is
kept separately.

In particular, usage of p3s clients - which would
be of interest to the end user -
is described in documents named appropriately, e.g.
the _job_ client is documented in JOB.md and its
PDF version which is JOB.pdf.

---

# Design notes
## Origin and prior documentation
**p3**s stands for "protoDUNE Prompt Processing System"
which has been created to support prompt (or "near-time/nearline")
processing necessary for Data Quality Monitoring (DQM) in
the protoDUNE experiment.

Supporting documents and an outline of the design can be found in
the FNAL DocDB 1861. Authorization is required for accessing this
resource.

To provide optimal and efficient user experience it is necessary
to keep track of multiple jobs in various stages of execution _and_
related units of data going through the system. That means the _state_
of these objects must be persisted (meaning there should be some sort of
a database) and also made available to the user via a GUI (meaning
there should be some sort of a web service). Thus there is a need
to provide a _web application_.

In principle, some of the existing Workload Management Systems such
as PanDA or Dirac could potentially be used to provide such functionality
but it was not an option for protoDUNE due to the steep learning curve,
complexity and potential integration difficulties. It was decided therefore
to create a purposely simple system with an absolute minimum of
functionality which however would still meet the requirements of the experiment.
Ease of deployment and maintenance were the main ctiteria. Some
ideas (e.g. the pilot framework approach and the monitoring web
service) were borrowed from the existing sytems.

## Components
The following components can be identified in p3s

* the server which includes a database back-end and a Web front-end

* a collection of clients which send messages to the server and
may receive replies

* service scripts that orchestrate execution of operations
necessary for continuous and optimal running of the system,
in most cases involving p3s clients; automation can be achieved
by including service scripts in crontab entries

For example, submission of a job defined by the user is accomplished
by running the appropriate client which sends a HTTP message to
the server containing all the information about the job that needs
to be executed.

## The Pilot Framework
The following problems must be solved in p3s:

* "just-in-time" execution, i.e. minimal latency of job execution after
it has been created. This could be a problem on most batch systems which
don't guarantee that

* ability to run on diverse, heterogenious and ad-hoc resources
(e.g. ad-hoc clusters at CERN, CERN Tier-0 and perhaps some other facilities)

* isolation of the execution environment from failures of worker nodes, and
other incidents that may occur at job initialization time

The above issues are addressed by using a pilot-based framework conceptually
similar to what is used in PanDA, DIRAC and other systems. In it, a pilot
job (agent) is deployed to the worker node and is registered on the system's
server. Independently, p3s users (or automated agents) send descriptions
of jobs that need to run which are also registered in the database.
A matching process take place where pilots that are available (i.e. not
busy) are matched to job records and actuate excution on the worker
node on which they are running. The pilot keeps track of the job state
and signals its completion or failure to the server, which is again
registered in the DB. All of these actions are reflected in the monitoring
web application so the user always has a picture of what's happening.

## Client/Server Architecture
The p3s server is a Web service i.e. its API is based on HTTP requests.
The user interacts with the system by means of clients which send HTTP requests to
the server. This is the only way to change the state of the server and the objects
it stores it its database.

The p3s server provides the following set of functionality:

* creates objects e.g. job records in its database, according to messages received
from clients which may be actuated by the user or run as a part of an automated script

* changes the state of objects - once again, according to messages coming from the clients

* monitoring of the state of various objects such as jobs, pilots, units of data etc

---

# p3s Objects
## The Pilot
The pilot process can be started on a worker node or a workstation
via a variety of methods (including interactive start by the user if necessary
but more commonly by a distributed shell or by a service which talks to the
batch system).
Once the pilot is live (and optionally performs a variety of possible checks) it
contacts the server, which then creates a record in its database. The record
reflects of state of the pilot as it goes through transitions.

An example of what states a pilot can go through during its lifecycle is given below:

* *active*: registered on the server, no attempt at brokerage yet

* *no jobs*: no jobs matched this pilot

* *dispatched*: got a job and preparing its execution (may still fail)

* *running*: running the payload job

* *finished*: job has completed

* *stopped*: stopped after exhausting all brokerage attempts.


## The Job
In the object sense, the p3s job is a record in its database which contains all information
necessary to create an actual process on a worker node. This record also reflects the status
of the object as it goes through transition.

## The Data
Currently p3s supports data units as individual files, in future development it may also
support the notion of dataset. Data (datasets) are registered on the p3s server by client
either actuated by the user or automated processes which create jobs and workflows when
fresh data arrives.


## The Workflow
Workflow model, interface and the corresponding p3s client are described in a separate document (*WORKFLOW.pdf*).


---

# p3s Clients

Most important of the p3s clients are:

   * The *pilot* - submission and management of pilot data on the server
   
   * The *job* - submission of job definitions to the server and management of job data on the server

   * The *dataset* - registration of data files in the system

Please see dedicated documents (e.g. "JOB") for more detail.

---

# Appendix
## p3s vs other systems

The p3s is the computing platform for protoDUNE to support Data Quality Management (DQM).
Its requirements and mode of operation are different from those of a typical Workload Management
System (such as used in offline production). In particular,

* there are specific ETA requirements ranging from minutes to tens of minutes
for various types of processing jobs since
for DQM purposes the results become stale (not actionable) rather fast

* only a portion of the data (configurable) needs to be processed; it is assumed
that the DAQ and its monitoring system provide stable data taking conditions
so it is not necessary to sample most of the data continuously. Further,
if necessary at run time, a portion of the data can be dropped (i.e. excluded from the DQM stream)
in any stage of processing in order to optimize throughput for critical jobs

* there is no retry/recovery mechanism for failing jobs since any substantial
delay in processing a unit of data makes the result less relevant. Instead,
output and error logs are recorded and used to debug jobs

* processing jobs/streams are initiated automatically and are triggered
by the data arriving from DAQ

* in p3s there is no distinct data handling system for two reasons. First, it is assumed
that p3s can access data either locally via a POSIX-like interface, or via XRootD
interface with minimal coding and integration effort. Second, a full-fledged data
handling system would introduce additional complexity, latency and potentially
failure modes. In summary, data handling capabilities are kept to an absolute minimum.

Due to above factors and to guarantee ease of operation, a simplified pilot-based
system was created as the core of p3s which leverages Django web application framework
and other existing tools, and includes a rather minimal amount of application-specific
code.


