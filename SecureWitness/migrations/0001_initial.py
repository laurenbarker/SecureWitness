# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('shortdesc', models.CharField(max_length=50)),
                ('longdesc', models.CharField(max_length=300)),
                ('location', models.CharField(max_length=50)),
                ('incident_date', models.DateField()),
                ('keywords', models.CharField(max_length=50)),
                ('private', models.BooleanField(default=False)),
                ('file', models.FileField(blank=True, null=True, upload_to='C:/Users/The F/PycharmProjects/forms/uploaded files')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='user',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
