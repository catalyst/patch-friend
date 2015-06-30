# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0002_auto_20150630_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostdiscoveryrun',
            name='finished',
            field=models.DateTimeField(null=True),
        ),
    ]
