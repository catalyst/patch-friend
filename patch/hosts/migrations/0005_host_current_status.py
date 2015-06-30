# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0004_auto_20150630_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='current_status',
            field=models.ForeignKey(related_name='+', default=None, to='hosts.HostStatus'),
            preserve_default=False,
        ),
    ]
