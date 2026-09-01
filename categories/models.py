from django.db import models

class Categories(models.Model):
    title = models.CharField(max_length=64, unique=True)
    

