# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='hostinfo_fingerprint',
            field=models.CharField(unique=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='hostdiscoveryrun',
            name='started',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
