# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0005_host_current_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='current_status',
            field=models.ForeignKey(related_name='+', to='hosts.HostStatus', null=True),
        ),
    ]
