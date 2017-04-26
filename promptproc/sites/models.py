import json
from django.db		import models
from django.core	import serializers

class site(models.Model):
    name	= models.CharField(max_length=64, default='', primary_key=True)		# human-readable site name
    env		= models.TextField(default='{}')			# the default site environment
    server	= models.CharField(max_length=64, default='')		# who the pilot talks to
    pilotcycles	= models.PositiveIntegerField(default=1)		#
    pilotperiod	= models.PositiveIntegerField(default=5)		# in seconds

    def __str__(self):
        return serializers.serialize("json", [self, ])
