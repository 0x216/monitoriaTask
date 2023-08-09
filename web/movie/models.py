from django.db import models

class Actor(models.Model):
    name = models.CharField(max_length=255)

class Movie(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    actors = models.ManyToManyField(Actor)