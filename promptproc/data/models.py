from django.db import models

# Dataset is a general class for a unit of data ingested or
# produced by a job. When using directed multigraph as the model fo
# workflow, this unit can remain just a file since multiple edges
# can exist between the vertices.
#
# "name" is a human-readable description - populated by "key" in
# networkx MultiDiGraph if coming from the client in GraphML format

class dataset(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    name	= models.CharField(max_length=64, default='')
    state	= models.CharField(max_length=64, default='')
    comment	= models.CharField(max_length=256, default='')
    datatype	= models.CharField(max_length=64, default='')

    wf		= models.CharField(max_length=64, default='')	# to which wf it belongs (name)
    wfuuid	= models.CharField(max_length=36, default='')

    sourceuuid	= models.CharField(max_length=36, default='')
    targetuuid	= models.CharField(max_length=36, default='')

    def __str__(self):
        return self.sourceuuid+':'+self.targetuuid


class datatype(models.Model):
    name	= models.CharField(max_length=64,	primary_key=True)
    ext		= models.CharField(max_length=8, default='')	# file extension
    comment	= models.CharField(max_length=256,	default='')

    
    def __str__(self):
        return self.name+':'+self.comment
