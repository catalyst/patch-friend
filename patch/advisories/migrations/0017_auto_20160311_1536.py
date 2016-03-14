# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0016_auto_20160311_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='severity'
        ),
        migrations.AddField(
            model_name='advisory',
            name='severity',
            field=models.IntegerField(default=0, help_text=b'Local severity of the advisory, once it has been reviewed', choices=[(0, b'Undecided'), (1, b'Low'), (2, b'Standard'), (3, b'High'), (4, b'Critical')]),
        ),
    ]
