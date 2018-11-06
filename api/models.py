from django.db import models

# Create your models here.
class Searches(models.Model):
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    count = models.IntegerField()
 