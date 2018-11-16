# Create your models here.
from django.db import models


class SliderImage(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=200)

    def __str__(self):
        return "Image : %s " % self.title


class Text(models.Model):
    type = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField()

    def __str__(self):
        return "Text %s pour %s " % (self.type, self.title)
