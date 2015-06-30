# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('advisories', '0012_auto_20150630_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisory',
            name='reviewed_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='advisory',
            name='severity',
            field=models.CharField(default=0, max_length=32, choices=[(0, b'Undecided'), (1, b'Low'), (2, b'Standard'), (3, b'High'), (4, b'Critical')]),
        ),
    ]
