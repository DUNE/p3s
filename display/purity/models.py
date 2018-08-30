import json
from django.db		import models
from django.core	import serializers


class pur(models.Model):
    run		= models.PositiveIntegerField(default=0,	verbose_name='Run')
    tpc		= models.PositiveIntegerField(default=0,	verbose_name='TPC')
    ts		= models.DateTimeField(blank=True,		verbose_name='Timestamp', null=True)
    lifetime	= models.FloatField(default=0.0,		verbose_name='LifeTime')
    error	= models.FloatField(default=0.0,		verbose_name='Error')
    count	= models.PositiveIntegerField(default=0,	verbose_name='Count')
    sn		= models.FloatField(default=0.0,		verbose_name='S/N')
    snclusters	= models.PositiveIntegerField(default=0,	verbose_name='S/N Clusters')
    drifttime	= models.FloatField(default=0.0,		verbose_name='DriftTime')

    def __str__(self):
        return serializers.serialize("json", [self, ])

    @classmethod
    def message(self):
        return ''
