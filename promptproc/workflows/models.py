from django.db import models

##################################### DAG #######################################################
# Workflow topology is a DAG:Edges correspond to data, Vertices correspond to jobs.
# When a DAG instantiated as a workflow, data and job objects are created. The DAG
# is like an abstract class for the Workflow.

class dag(models.Model):
    _init = False
    name	= models.CharField(max_length=64, primary_key = True, default='')
    description	= models.TextField(default='')
    nvertices	= models.IntegerField(default=0, null=False)
    root	= models.CharField(max_length=64, default='')
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)	# definition
   

    def __str__(self):
        return self.name

# -------
class dagVertex(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs
    
    def __str__(self):
        return self.name

# -------
class dagEdge(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs

    source	= models.CharField(max_length=36, default='')	# source
    target	= models.CharField(max_length=36, default='')	# target
    
    def __str__(self):
        return self.source+':'+self.target


####################################  WORKFLOW ##################################################
class workflow(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    name	= models.CharField(max_length=64, default='')	# not expected to be unique
    description	= models.TextField(default='')
    dag		= models.CharField(max_length=64, default='')	# dag name (as a type of wf)
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)	# definition
    
    def __str__(self):
        return self.name
# -------
class wfVertex(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    wf		= models.CharField(max_length=64, default='')	# to which wf it belongs
    wfuuid	= models.CharField(max_length=36, default='')
    
    def __str__(self):
        return self.name
# -------
class wfEdge(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    wf		= models.CharField(max_length=64, default='')	# to which wf it belongs
    wfuuid	= models.CharField(max_length=36, default='')

    source	= models.CharField(max_length=36, default='')	# source
    target	= models.CharField(max_length=36, default='')	# target
    
    def __str__(self):
        return self.source+':'+self.target

