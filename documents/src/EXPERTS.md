Created by: Maxim Potekhin        _potekhin@bnl.gov_

# Release Notes

* Version 1.01 20180922 first official version

---

# Introduction

This document is of interest to a small group of people who
have enough expertise and system access rights to perform
mission-critical updates, service restarts and similar actions
on the protoDUNE p3s and DQM servers. You will need to obtain
credentials for the protoDUNE DQM production account. If you
are not a member of this group of expert DQM users you don't
have to read this document any further.

This document is maintaned in the "markdown" format and the source file
is contained in the directory *p3s/documents/src*. To rebuild the PDF
version as needed you can use the command (provided you have pandoc
installed):

```
pandoc -s -o EXPERTS.pdf EXPERTS.md
```

# Servers

## The machines
There are three VMs running within the CERN OpenStack cloud:

* **p3s-web.cern.ch** - the workload management server which orchestrates the execution of DQM jobs in CERN Tier-0 (''lxbatch'') and has extensive monitoring capabilities via its Web UI.
* **p3s-content.cern.ch** - content management service which allows users to browse and query data products created by the DQM jobs which have run in the p3s framework via its Web UI.
* **p3s-db.cern.ch** - the database server running PostgreSQL which is the critical DB backend for both *p3s-web* and *p3s-content*.

You can access these machines with credentials assigned to the production account *np04dqm*. These can be obtained -  on need-only basis - from Nektarios Benekos
as authorized by DQM leaders. The user *np04dqm* has *sudo* priviledges on these three machines.

The first two servers run Apache-Django services which may need to be updated, stopped, started or restarted.

## Maintenance

It's a good practice to periodically check the available disk space once every few weeks, even though
problems are not anticipated in this area. Theoretically, there may be unusually "fat" Apache logs
and other leftovers that may need cleaning. The Linux load report for p3s-web is presented on the
landing page of that service, and if the load appears to be too high adjustments may be needed such
as reducing the frequency interaction of the p3s pilots with the service. This is usually not necessary
if there are only a few hundred pilots running (200-300) but may become an issue at the pilot population
of over a thousand. The number of running pilots is readily available on the landing page.

## Updates

The database server p3s-db does not need updates.

The p3s and DQM servers are updated in the following way - the users issues
the "git pull" command in the directory "~/projects/p3s" and then the Apache server needs a restart. There is an alias
on both machines under the name *arestart* (for "Apache Restart") which will ask for the user's password. The user must
be under the identity of *np04dqm*.

If a server tanks (which happens exceedingly rarely and not expected during the run) you will just need
to restart.

# Crontab

There are a few service processes that allow p3s/DQM to run according to the design. These run
periodically as directed by crontab entries defined by the user *np04dqm*.



