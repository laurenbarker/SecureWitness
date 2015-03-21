# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_report_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='author',
        ),
    ]
