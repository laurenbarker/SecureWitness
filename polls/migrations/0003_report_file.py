# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20150320_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='C:/Users/The F/PycharmProjects/forms/uploaded files'),
            preserve_default=True,
        ),
    ]
