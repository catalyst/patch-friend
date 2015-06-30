# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0009_auto_20150626_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='binarypackage',
            name='safe_version',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
