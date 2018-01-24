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
