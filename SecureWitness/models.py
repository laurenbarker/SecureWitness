from django.db import models
import json
import os

class user(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    adminStatus = models.IntegerField(default=0)
    suspensionStatus = models.IntegerField(default=0)
    def __str__(self):
        return self.username

class report(models.Model):
    author = models.ForeignKey(user, default = 1)
    timestamp = models.DateTimeField(auto_now_add=True)
    shortdesc = models.CharField(max_length=50)
    longdesc = models.CharField(max_length=300)
    location = models.CharField(max_length=50, blank = True, null=True)
    incident_date = models.DateField(blank = True, null=True)
    keywords = models.CharField(max_length=50, blank = True, null=True)
    private = models.BooleanField(default=False)
    folder = models.CharField(max_length=50, blank = True, null = True)
    group = models.CharField(max_length=500, blank = True)
#change this line to save files somewhere else
    file = models.FileField(upload_to='staticfiles',null = True, blank = True)
    key = models.CharField(blank = True, max_length=2048)
    def __str__(self):
        return   "Report Number: " + str(self.id) + " Short Description: " + self.shortdesc


class group(models.Model):
    users = models.CharField(max_length=500, blank=True)
    groupName = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.groupName
