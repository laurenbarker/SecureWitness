from django.contrib import admin

# Register your models here.
from django.contrib import admin
from polls.models import report
from polls.models import user

admin.site.register(report)
admin.site.register(user)