# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0003_auto_20150630_1610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hoststatus',
            options={'verbose_name_plural': 'host statuses'},
        ),
        migrations.RenameField(
            model_name='hostdiscoveryrun',
            old_name='started',
            new_name='created',
        ),
        migrations.RemoveField(
            model_name='hostdiscoveryrun',
            name='finished',
        ),
        migrations.AddField(
            model_name='hoststatus',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 5, 9, 50, 876799, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
