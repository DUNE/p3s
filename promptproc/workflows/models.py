from django.db import models

# Workflow topology as a DAG:
# Edges correspond to data, Vertices correspond to jobs.
# When a DAG instantiated as a workflow, data and job objects are created.

class dagEdge(models.Model):
    source	= models.CharField(max_length=36, default='')		# source
    target	= models.CharField(max_length=36, default='')		# target
    name	= models.CharField(max_length=64, default='')		# human-readable description
    
    def __str__(self):
        return self.source+':'+self.target


