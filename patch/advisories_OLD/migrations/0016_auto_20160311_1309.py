# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0015_auto_20160302_1416'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advisory',
            options={'ordering': ['-issued'], 'verbose_name_plural': 'advisories'},
        ),
        migrations.AlterModelOptions(
            name='binarypackage',
            options={'ordering': ['-package'], 'verbose_name_plural': 'binary packages'},
        ),
        migrations.AlterModelOptions(
            name='sourcepackage',
            options={'ordering': ['-package'], 'verbose_name_plural': 'source packages'},
        ),
    ]
