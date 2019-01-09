#
# This is the class to account for and make accessible ANY type of DQM results
# as long as they supply valid JSON describing the data
#

import json

from django.db			import models
from django.core		import serializers
from django.utils.safestring	import mark_safe

################################################################################################
class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0,	verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0,	verbose_name='SubRun')
    dl		= models.PositiveIntegerField(default=0,	verbose_name='dl')
    summary	= models.TextField(default='{}',		verbose_name='Summary')
    description	= models.TextField(default='{}',		verbose_name='Description')
    j_uuid	= models.CharField(max_length=36, default='',	verbose_name='Produced by job')
    ts		= models.DateTimeField(blank=True,null=True,	verbose_name='Timestamp')
    jobtype	= models.CharField(max_length=16, default='',	verbose_name='Job Type')
    directory	= models.TextField(default='2019_01',		verbose_name='Directory')
    # The above default value is a temporary solution but a workable one.
    # We don't cut new directories often,
    # so having this in the code is not too burdensome
 
    # ---
    @classmethod
    def autoMonLink(self, domain, run, subrun, dl, jobtype, category, filetype):
        pattern = '<a href="http://%s/monitor/automon?run=%s&subrun=%s&dl=%s&jobtype=%s&category=%s&filetype=%s">%s</a>'
        link = mark_safe(pattern % (domain, run, subrun, dl, jobtype, category, filetype, filetype))
        return link

    # ---
    @classmethod
    def backMonLink(self,domain,run,subrun,jobtype):
        pattern = '<a href="http://%s/monitor/automon?run=%s&subrun=%s&jobtype=%s">Back to %s::%s::%s</a>'
        link = mark_safe(pattern % (domain, run, subrun, jobtype, run, subrun, jobtype ))
        return link

    # ---
    # This used to be a classmethod, but now we use actual content of the "directory" attribute
    def autoMonImgURLs(self, domain, dqmURL, j_uuid, files):
        fList, row, rows, cnt = files.split(','), [], [], 0

        for filename in fList:
            row.append('http://%s/%s/%s/%s/%s' % (domain, dqmURL, self.directory, j_uuid, filename))
            cnt+=1
            if cnt==6:
                cnt=0
                rows.append(row)
                row = []
        if(len(row)>0): rows.append(row) #!
        return rows

################################################################################################

