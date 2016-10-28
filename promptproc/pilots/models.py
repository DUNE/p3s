from django.db import models

# Create your models here.
class pilot(models.Model):
    cluster	= models.CharField(max_length=32)
    host	= models.CharField(max_length=32)
    uuid	= models.CharField(max_length=32, default='')
    ts_created	= models.DateTimeField('ts_cre', blank=True, null=True)
    ts_reg	= models.DateTimeField('ts_reg', blank=True, null=True)

    # time autofill:
    #    auto_now=True
    
    def __str__(self):
        return self.cluster
