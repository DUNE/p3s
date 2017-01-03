# p3s inputs

# Jobs
The files name "job_template*" are meant to be used with the script
like "job" in the p3pilot directory, which interact with the server.
They allow the user to inject the database with multiple job
definitions at once, from a single file. The syntax is currently:
`
python3 job.py -j mytemplates.json
`

The template file is supposed to represent a JSON list.

# Workflows and DAGs
A DAG is supposed to serve as a template for an instance
of workflow. DAGs can be stored in a few formats, for now we stick with GraphML
which is fairly standard and importantly can be parsed by the Networkx package.

By default edges and nodes in a workflow inherit properties of the DAG the workflow
is derived from, but they can also be overwritten by supplying a JSON string or
a JSON file in the format
`
{"my":{"foo":"bar"}}
`
where "my" is the name of the object (node or edge in which case it will look like "source:target"
with actual names of the source and target"), and the dictionary within lists the attributes to
be defined when the client is run (such as "workflow.py").

