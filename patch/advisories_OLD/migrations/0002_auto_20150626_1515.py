# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='advisory',
            options={'verbose_name_plural': 'advisories'},
        ),
        migrations.AddField(
            model_name='advisory',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisory',
            name='issued',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 26, 3, 15, 56, 624142, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
