import json
from django.db		import models
from django.core	import serializers


class evdisp(models.Model):
    run		= models.PositiveIntegerField(default=0)
    subrun	= models.PositiveIntegerField(default=0)
    evnum	= models.PositiveIntegerField(default=0)
    changroup	= models.PositiveIntegerField(default=0) # there are six channel groups
    ts		= models.DateTimeField('ts', blank=True, null=True)
    lifetime	= models.FloatField('lifetime', default=0.0)
    error	= models.FloatField('error', default=0.0)
    count	= models.PositiveIntegerField(default=0)

    def __str__(self):
        return serializers.serialize("json", [self, ])

# Channel groups:
# ch0-2559.png
# ch2560-4639.png
# ch5120-7679.png
# ch7680-9759.png
# ch10240-12799.png
# ch12800-14879.png
