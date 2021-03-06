from django.db import models

##################################### DAG #######################################################
# Workflow topology is a DAG:Edges correspond to data, Vertices correspond to jobs.
# When a DAG instantiated as a workflow, data and job objects are created. The DAG
# is like an abstract class for the Workflow.

class dag(models.Model):
    _init = False
    name	= models.CharField(max_length=64, primary_key = True, default='')
    user	= models.CharField(max_length=64, default='')		# who designed the dag
    description	= models.TextField(default='')
    nvertices	= models.IntegerField(default=0, null=False)
    root	= models.CharField(max_length=64, default='')		# id of the tree root
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)	# time of definition

    def __str__(self):
        return self.name

# -------
class dagVertex(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs
    jobtype	= models.CharField(max_length=16, default='')
    payload	= models.CharField(max_length=256,default='')	# provisional, url/path
    env		= models.TextField(default='{}')
    timelimit	= models.PositiveIntegerField(default=1000)	# in seconds
    priority	= models.PositiveIntegerField(default=0)	# higher wins

    def __str__(self):
        return self.name

# -------
class dagEdge(models.Model):
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs
    name	= models.CharField(max_length=64, default='')	# a filename or a placeholder for one
    dirpath	= models.CharField(max_length=256,default='')
    
    comment	= models.CharField(max_length=256, default='')
    datatype	= models.CharField(max_length=64, default='')
    datatag	= models.CharField(max_length=64, default='')

    source	= models.CharField(max_length=64, default='')	# source
    target	= models.CharField(max_length=64, default='')	# target
    
    def __str__(self):
        return self.source+':'+self.target


####################################  WORKFLOW ##################################################
# As opposed to DAG (which is abstract) the workflow contains actual jobs and data elements
class workflow(models.Model):
    uuid	= models.CharField(max_length=36,	default='')
    user	= models.CharField(max_length=64,	default='')	# who submitted the workflow
    state	= models.CharField(max_length=64,	default='')
    comment	= models.TextField(default='')				# may include failure report
    rootuuid	= models.CharField(max_length=36, 	default='')	# handle on the 1st job
    name	= models.CharField(max_length=64,	default='')	# not expected to be unique
    description	= models.TextField(default='')
    dag		= models.CharField(max_length=64,	default='')	# dag name (as a type of wf)
    state	= models.CharField(max_length=16,	default='')	#
    ts_def	= models.DateTimeField('ts_def',	blank=True, null=True)	# definition
    ts_sta	= models.DateTimeField('ts_sta',	blank=True, null=True)	# start
    ts_sto	= models.DateTimeField('ts_sto',	blank=True, null=True) # stop
    nvertices	= models.IntegerField(default=0,	null=False)
    ndone	= models.IntegerField(default=0,	null=False)
    
    @classmethod
    def N(self):
        return self.objects.count()

    def __str__(self):
        return self.name


