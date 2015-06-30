# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0006_auto_20150630_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='hostinfo_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_fingerprint',
            field=models.CharField(max_length=200, unique=True, null=True),
        ),
    ]
