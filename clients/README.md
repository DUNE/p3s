# p3s clients
There are the following major classes in p3s:
* job
* pilot
* dataset
* workflow

There are also a few companion classes whose definition is typically
contained in the same unit of code as the major class. By and large,
the classes itemized above are described in the respective "model.py"
files under their own Django app areas.

Example - the follwing file:
`/mydir/p3s/promptproc/workflows/models.py`
...contains the class "workflow", which inherits from the Django Model class.
Same pattern applies to other classes.

# job.py

This client is used to:
* create a job (or a number of jobs) on the server. By default standalone jobs
are created, which are not associated with a workflow. This can be done by reading a description of
job(s) contained in a JSON file. An example (with arbitrary names and variables demonstrates
how JSON is used:
`[
    {
        "name":         "p3s_job",
        "timeout":      "100",
        "jobtype":      "type1",
        "payload":      "/home/p3s/my_executable.py",
        "env":          {"P3S":"TRUE","MYVAR":"FALSE"},
        "priority":     "1",
        "state":        "defined"
    }
]`

* adjust job attributes
* delete a job from the server

# pilot.py

Generates a pilot and performs a small number of other functions.
The lifecycle of a pilot is as follows:
* The process starts and attempts to contact the server in order to register. At the time of writing
handling timeouts is not imeplemented yet, i.e. the pilot will exit in fail condition if there is not
response from the server. This behavior will be improved in future development.

* Upon successful registration, the pilot enters a loop. In each iteration it send a job request
to the server. If the request is not granted, the pilot sleeps for a configurable period of time
and make another attempts. Having exhausted the maximal number of attempts (configurable), the pilot
exits normally.

* Upon receiving a successful match from the server, the pilot initiates job execution using
the Python "subprocess" machinery.
