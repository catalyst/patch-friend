# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0009_hostimportedattribute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='key',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='value',
            field=models.CharField(max_length=200),
        ),
    ]
