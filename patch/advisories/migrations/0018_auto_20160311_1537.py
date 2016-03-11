# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0017_auto_20160311_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='search_binary_packages',
        ),
        migrations.RemoveField(
            model_name='advisory',
            name='search_source_packages',
        ),
        migrations.AddField(
            model_name='advisory',
            name='search_packages',
            field=models.TextField(help_text=b'Space separated list of source and binary packages used to speed up search', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b'Person who locally reviewed the advisory for its overall severity (or None if the severity was determined automatically)', null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='severity',
            field=models.IntegerField(default=0, help_text=b'Local severity of the advisory, once it has been reviewed', blank=True, choices=[(0, b'Undecided'), (1, b'Low'), (2, b'Standard'), (3, b'High'), (4, b'Critical')]),
        ),
    ]
