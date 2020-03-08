from django.db import models


# Create your models here.
class mask_DB(models.Model) :
    content = models.CharField(max_length = 255)