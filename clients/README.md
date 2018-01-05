# p3s clients
## Overview of principal client apps in p3s
The p3s object model contains the following major classes:
* job
* pilot
* dataset
* workflow

The clients carrying similar names have the function of managing
objects which belong to their respective classes wnd which reside on the server:

* job.py
* pilot.py
* dataset.py
* workflow.py

The server API which all of these scripts use is encapsulated in
the module "serverAPI.py" described in one of the sections below.

