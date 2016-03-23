# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0018_host_source'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'host', 'architecture')]),
        ),
    ]
