# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0012_auto_20150702_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='tags',
            field=models.ManyToManyField(to='hosts.Tag'),
        ),
    ]
