import json
from django.db		import models
from django.core	import serializers


class pur(models.Model):
    run		= models.PositiveIntegerField(default=0)
    tpc		= models.PositiveIntegerField(default=0)
    ts		= models.DateTimeField('ts', blank=True, null=True)
    lifetime	= models.FloatField('lifetime', default=0.0)
    error	= models.FloatField('error', default=0.0)
    count	= models.PositiveIntegerField(default=0)

    def __str__(self):
        return serializers.serialize("json", [self, ])
