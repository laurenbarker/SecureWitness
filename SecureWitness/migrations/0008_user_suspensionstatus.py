# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0007_auto_20150401_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='suspensionStatus',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
