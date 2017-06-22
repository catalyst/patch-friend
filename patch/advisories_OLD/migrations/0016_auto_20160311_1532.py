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
        migrations.AddField(
            model_name='advisory',
            name='search_binary_packages',
            field=models.TextField(help_text=b'Space separated list of binary packages used to speed up search', null=True),
        ),
        migrations.AddField(
            model_name='advisory',
            name='search_source_packages',
            field=models.TextField(help_text=b'Space separated list of source packages used to speed up search', null=True),
        ),
    ]
