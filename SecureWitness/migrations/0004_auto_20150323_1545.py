# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0003_auto_20150323_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='incident_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='keywords',
            field=models.CharField(null=True, blank=True, max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='location',
            field=models.CharField(null=True, blank=True, max_length=50),
            preserve_default=True,
        ),
    ]
