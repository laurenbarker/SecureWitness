from django.db import models

class user(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    adminStatus = models.IntegerField(default=0)
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
#change this line to save files somewhere else
    file = models.FileField(upload_to='C:/Users/The F/PycharmProjects/forms/uploaded files', null = True, blank = True)
    def __str__(self):
        return self.shortdesc