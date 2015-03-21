from django.db import models

# Create your models here.
from django.db import models


class user(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.username

class report(models.Model):
    #author = models.ForeignKey(user)
    timestamp = models.DateTimeField(auto_now_add=True)
    shortdesc = models.CharField(max_length=50)
    longdesc = models.CharField(max_length=300)
    location = models.CharField(max_length=50)
    incident_date = models.DateField()
    keywords = models.CharField(max_length=50)
    private = models.BooleanField(default=False)
#change this line to save files somewhere else
    file = models.FileField(upload_to='C:/Users/The F/PycharmProjects/forms/uploaded files', null = True, blank = True)
    def __str__(self):
        return self.shortdesc