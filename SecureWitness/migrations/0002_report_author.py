# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='author',
            field=models.ForeignKey(default=1, to='SecureWitness.user'),
            preserve_default=True,
        ),
    ]
