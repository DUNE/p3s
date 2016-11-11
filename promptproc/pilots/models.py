from django.db import models

# Create your models here.
class pilot(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    state	= models.CharField(max_length=16, default='')
    cluster	= models.CharField(max_length=32)
    host	= models.CharField(max_length=32)
    ts_created	= models.DateTimeField('ts_cre', blank=True, null=True)
    ts_reg	= models.DateTimeField('ts_reg', blank=True, null=True)

    # time autofill:
    #    auto_now=True
    
    def __str__(self):
        return self.uuid
