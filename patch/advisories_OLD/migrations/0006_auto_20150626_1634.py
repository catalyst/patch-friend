# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0005_auto_20150626_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisory',
            name='issued',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
