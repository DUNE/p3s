import json
from django.db import models
from django.core	import serializers
from django.utils.safestring		import mark_safe

################################################################################################
class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0,	verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0,	verbose_name='SubRun')
    summary	= models.TextField(default='{}',		verbose_name='Summary')
    description	= models.TextField(default='{}',		verbose_name='Description')
    j_uuid	= models.CharField(max_length=36, default='',	verbose_name='Produced by job')
    ts		= models.DateTimeField(blank=True,null=True,	verbose_name='Timestamp')
    jobtype	= models.CharField(max_length=16, default='',	verbose_name='Job Type')
 
    # ---
    @classmethod
    def autoMonLink(self,domain,run,subrun,jobtype,category,filetype):
        pattern = '<a href="http://%s/monitor/automon?run=%s&subrun=%s&jobtype=%s&category=%s&filetype=%s">%s</a>'
        link = mark_safe(pattern % (domain, run, subrun, jobtype, category, filetype, filetype))
        return link
    # ---
    @classmethod
    def backMonLink(self,domain,run,subrun,jobtype):
        pattern = '<a href="http://%s/monitor/automon?run=%s&subrun=%s&jobtype=%s">Back to %s::%s::%s</a>'
        link = mark_safe(pattern % (domain, run, subrun, jobtype, run, subrun, jobtype ))
        return link
    # ---
    @classmethod
    def autoMonImgURLs(self, domain, dqmURL, j_uuid, files):
        fList, row, rows, cnt = files.split(','), [], [], 0

        for filename in fList:
            row.append('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
            cnt+=1
            if cnt==6:
                cnt=0
                rows.append(row)
                row = []
        if(len(row)>0): rows.append(row) #!
        return rows

################################################################################################
#class monrun(models.Model):
