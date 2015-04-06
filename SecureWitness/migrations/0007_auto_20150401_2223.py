# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0006_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='group',
        ),
        migrations.AddField(
            model_name='group',
            name='groupName',
            field=models.CharField(max_length=100, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='group',
            name='users',
            field=models.CharField(max_length=500, blank=True),
            preserve_default=True,
        ),
    ]
