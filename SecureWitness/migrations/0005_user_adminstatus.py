# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SecureWitness', '0004_auto_20150323_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='adminStatus',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
