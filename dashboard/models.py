from django.db import models

# Create your models here.
# models.py
class DAGNode(models.Model):
    name = models.CharField(max_length=50)
   

