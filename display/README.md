# Presentation subsystem for the protoDUNE Data Quality Monitor

This service currently runs on the machine "p3s-content" at CERN.

The apps in the monitor are structure like this:
* monitor - contains "views" for a few different functionalities, i.e. this is the place where the monitoring pages are created. Incidentally it also manages data produced by the TPC/SSP "monitor" app.
* purity - manages the Purity Monitor data
* evdisp - manages the Event Display data

The folder "dqm": the main "application" i.e. the location of settings.py

