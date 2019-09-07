from django.db import models

# Create your models here.


class NewModel(models.Model):
    test = models.BooleanField(default=True)