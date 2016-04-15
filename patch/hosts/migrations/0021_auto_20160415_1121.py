# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0020_auto_20160323_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='host',
            name='status',
        ),
        migrations.RemoveField(
            model_name='package',
            name='status',
        ),
    ]
