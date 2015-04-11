# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0010_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='group',
            field=models.CharField(blank=True, max_length=500),
            preserve_default=True,
        ),
    ]
