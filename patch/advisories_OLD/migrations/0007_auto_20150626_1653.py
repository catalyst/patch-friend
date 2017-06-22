# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0006_auto_20150626_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='binarypackage',
            name='source_package',
            field=models.ForeignKey(default=0, to='advisories.SourcePackage'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='advisory',
            name='issued',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
