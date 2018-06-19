import json
from django.db import models
from django.core	import serializers

class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0, verbose_name='SubRun')
    summary	= models.TextField(default='{}')

