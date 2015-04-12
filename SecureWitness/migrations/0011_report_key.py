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
            name='key',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
