# Workflow
## DAG
A worfklow _template_ is called "DAG" for brevity. Indeed,
is it a DAG but it does not contain references to concrete
payloads and/or datasets. In the current version of p3s the name
of the DAG is unique. Any change to the DAG content no matter how small
requires creation of a new DAG under a different name, for sake of
referential integrity.

## Workflow
A workflow is an instance of a particular DAG and
it is created using a pre-existing DAG as a template. It contains
references to concrete payloads and their parameters, however
the edges of the workflow (which is also a graph) represent data and
not all data may be avaialble when a workflow is instantiated.
For that reasons, data sets (edges in the graph) are augmented
as the workflow gets executed.

By the time a workflow is created the names of all nodes and
edged (i.e. jobs and data) are finalized regardless of their
state. The states of the nodes and edges are updated as
the workflow progresses.

