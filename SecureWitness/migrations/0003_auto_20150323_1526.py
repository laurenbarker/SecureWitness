# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0002_report_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='incident_date',
            field=models.DateField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='keywords',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='location',
            field=models.CharField(max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
