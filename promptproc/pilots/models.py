from django.db import models


# pilot timestamps:
# created, registered, last heartbeat

class pilot(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    state	= models.CharField(max_length=16, default='')
    site	= models.CharField(max_length=32)
    host	= models.CharField(max_length=32)
    ts_cre	= models.DateTimeField('ts_cre', blank=True, null=True)
    ts_reg	= models.DateTimeField('ts_reg', blank=True, null=True)
    ts_lhb	= models.DateTimeField('ts_lhb', blank=True, null=True)

    # time autofill:
    #    auto_now=True
    
    def __str__(self):
        return self.uuid
