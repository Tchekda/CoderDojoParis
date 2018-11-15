from django.db import models

# Create your models here.

class Mail(models.Model):
    type = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()