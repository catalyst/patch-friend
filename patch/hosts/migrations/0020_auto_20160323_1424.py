# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import hosts.models


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0019_auto_20160323_1356'),
    ]

    operations = [
        migrations.RunSQL(
            'CREATE EXTENSION debversion;',
            'DROP EXTENSION debversion;',
        ),
        migrations.AlterField(
            model_name='package',
            name='version',
            field=hosts.models.DebversionField(help_text=b"The package manager's version for this package.", max_length=200),
        ),
    ]
