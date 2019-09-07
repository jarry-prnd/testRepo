from django.db import models


class TestNewModel(models.Model):
    test = models.BooleanField(default=True)
    test2 = models.BooleanField(default=True)