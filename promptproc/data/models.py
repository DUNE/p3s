from django.db import models

# Dataset is a general class for a collection of files ingested or
# produced by a job
class dataset(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    name	= models.CharField(max_length=64, default='')	# human-readable description
    wf		= models.CharField(max_length=64, default='')	# to which wf it belongs (name)
    wfuuid	= models.CharField(max_length=36, default='')

    sourceuuid	= models.CharField(max_length=36, default='')
    targetuuid	= models.CharField(max_length=36, default='')

    def __str__(self):
        return self.sourceuuid+':'+self.targetuuid

