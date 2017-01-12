# Options
For brief summary of command line options run the script with "--help" option.

# Terminology
DAG is an abstraction of a workflow i.e. it describes its topology
and general characteristics of edges and vertices but does not
correspond to a running process nor does it have a complete information
to create a functional workflow. Workflows are created based on DAGs
serving as templates.

# DAG definition
Option "-g" allows to use a graphML file containing a DAG description
and send it to the server. A name can be suppplied via a command line
argument, and if absent it is derived from the name of the file containing
the graph.

DAG names are unique which is enforced in the database.

# Workflow definitions

Workflows are created based on templates (DAGs) which must be
exist on the server by the time a request for a new workflow is sent.
A name can be optionally set for a workflow but it's not expected
to be unique. Worflows are identified in the system by their UUIDs which
are automatically generated.

# Object Deletion

Until serious testing has been completed, please consult the experts
about this, such as the author of this software - especially
if the system is in production.

# File Info

By default, p3s will create filenames for a workflow dynamically utilizing
UUID and a predefined extension as per the declared data type. This can
be changed by using The option "-f" which is is overloaded and can be:

* a stirng not formatted in JSON and taking values such as:
   * "sticky", in which case a workflow inherits the file names from its parent DAG
   * "inherit:name", in which case filenames will be automatically generated based on the supplied name and DAG topology
      
* a JSON-formatted string which can specify the filenames for any of the DAG's edges if desired
* a name of a JSON file containing same information

# Job Info

It works similar to "file info" explained above. Information supplied in JSON format (either on the command line
or in a file supplied with -j option and having json extension will be included in the job object on the server side.

# Example
`./workflow.py -v 2 -a source1 -n sourceTest -s defined -f ../inputs/fileinfo1.json -j '{"filter":{"payload":"env"}}'`

