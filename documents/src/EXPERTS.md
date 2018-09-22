Created by: Maxim Potekhin        _potekhin@bnl.gov_

# Release Notes

* Version 1.01 20180922 first official version

---

# Introduction
## Purpose of this document
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

## Servers

* '''p3s-web.cern.ch''' - the workload management server which orchestrates the execution of DQM jobs in CERN Tier-0 (''lxbatch'')
* '''p3s-content.cern.ch''' - content management service which allows users to browse and query data products created by the DQM jobs which have run in the p3s framework.



