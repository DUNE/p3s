import json
from django.db		import models
from django.core	import serializers

class site(models.Model):
    name	= models.CharField(max_length=64, default='', primary_key=True)		# human-readable site name
    env		= models.TextField(default='{}')			# the default site environment
    server	= models.CharField(max_length=64, default='')		# who the pilot talks to
    pilotcycles	= models.PositiveIntegerField(default=1)		#
    pilotperiod	= models.PositiveIntegerField(default=10)		# in seconds
    pilotbeat	= models.PositiveIntegerField(default=20)		# in seconds

    def __str__(self):
        return serializers.serialize("json", [self, ])

    @classmethod
    def N(self):
        return self.objects.count()
    
    @classmethod
    def list(self):
        l = []
        for s in self.objects.all(): l.append(s.name)
        return l
