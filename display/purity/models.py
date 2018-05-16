import json
from django.db		import models
from django.core	import serializers


class pur(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    tpc		= models.PositiveIntegerField(default=0, verbose_name='TPC')
    ts		= models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')
    lifetime	= models.FloatField(default=0.0, verbose_name='LifeTime')
    error	= models.FloatField(default=0.0, verbose_name='Error')
    count	= models.PositiveIntegerField(default=0, verbose_name='Count')

    def __str__(self):
        return serializers.serialize("json", [self, ])
