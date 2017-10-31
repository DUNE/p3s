from django.db import models

# Create your models here.
class stats(models.Model):
    j= models.CharField(max_length=36, default='')
    
    def __str__(self):
        return self.j
