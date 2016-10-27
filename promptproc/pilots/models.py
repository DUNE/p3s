from django.db import models

# Create your models here.
class pilot(models.Model):
    cluster	= models.CharField(max_length=20)
    host	= models.CharField(max_length=40)
    ts_reg	= models.DateTimeField('ts_def', auto_now=True)

    
    def __str__(self):
        return "pilot"
