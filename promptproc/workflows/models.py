from django.db import models

##################################### DAG ##########################################################
# Workflow topology is a DAG:Edges correspond to data, Vertices correspond to jobs.
# When a DAG instantiated as a workflow, data and job objects are created. The DAG
# is like an abstract class for the Workflow.

class dag(models.Model):
    _init = False
    name	= models.CharField(max_length=64, default='')		# human-readable description
   

    def __str__(self):
        return self.name


class dagVertex(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs
    
    def __str__(self):
        return self.name

class dagEdge(models.Model):
    name	= models.CharField(max_length=64, default='')	# human-readable description
    dag		= models.CharField(max_length=64, default='')	# to which dag it belongs

    source	= models.CharField(max_length=36, default='')	# source
    target	= models.CharField(max_length=36, default='')	# target
    
    def __str__(self):
        return self.source+':'+self.target


####################################  WORKFLOW #####################################################
class workflow(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    name	= models.CharField(max_length=64, default='')	# not expected to be unique
    dag		= models.CharField(max_length=64, default='')	# dag name (as a type of wf)
    
    def __str__(self):
        return self.name

