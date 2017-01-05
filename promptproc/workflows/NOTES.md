# Workflow logic
## Intro
These notes explain some of the terminology used in the
workflow section of p3s.

## DAG
A worfklow template is called "dag" for brevity. Indeed,
is it a DAG.It does not contain references to concrete
payloads and/or datasets.

## Workflow
A workflow is an instance of a particular DAG, or it can be said that
it's created based on a template which is a DAG.It contains
references to concrete payloads and their parameters, however
the edges of the workflow (which is also a graph) represent data and
not all data may be avaialble when a workflow is instantiated.
For that reasons, data sets (edges in the graph) are augmented
as the workflow gets executed.
