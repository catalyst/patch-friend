# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0013_host_tags'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='hostimportedattribute',
            unique_together=set([('host', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'host')]),
        ),
        migrations.AlterUniqueTogether(
            name='packagestatus',
            unique_together=set([('package', 'discovery_run')]),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'customer')]),
        ),
    ]
