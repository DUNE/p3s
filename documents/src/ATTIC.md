# PLEASE DISREGARD THIS FILE, IT'S USED AS AN EDIT BUFFER

* Use a dedicated client ("job.py") to submit this job description to the server which will then orchestrate its execution

* Monitor the progress of jobs using a P3S Web page

* Browse and use the output files produced by jobs

In the following we assume that the CERN instance of P3S is used, which entails
certain conventions and conviences such as sharing files and scripts via AFS and EOS.

# P3S Clients

## job.py

This client can be used for the following:

* send a job description (or a number of job descriptions) to the P3S server.
This can be done by reading a description of job(s) contained in a JSON file.

* if necessary, adjust job attributes

* delete a job from the server


---

This won't work out of the box for you since it contains references to particular
paths which are very likely invalid on your system. So it needs to be tweaked
a little:

* please copy this file and edit your copy so that it points to the actual location of the _payload_ script (which must be
readable by the np04-comp group)

* likewise, when making edits please make sure that the input file location is readable to members of _np04-comp_ group at CERN (or just globally readable) and the path to the output file can likewise be used (i.e. must be writeable).

Note: while the "payload script" is named "simplejob1.sh" in this case , the
exact name is actually unimportant and can be changed, that's just what it is in this
particular JSON template
```
#!/bin/bash

echo pid, ppid: $$ $PPID

if [ -z ${P3S_INPUT_FILE+x} ];
then
    echo No input file specified, entering sleep mode
    /bin/sleep 10
    exit
fi


echo Using input file $P3S_INPUT_FILE

wc -l $P3S_INPUT_FILE > $P3S_OUTPUT_FILE
```

It is important that the path to simplejob1.sh is _readable and executable_ for other users,
otherwise the system won't be able to run it. For example, in **lxplus** it is optimally placed
in the "public" subdirectory in your account which is on AFS and is open to public.

