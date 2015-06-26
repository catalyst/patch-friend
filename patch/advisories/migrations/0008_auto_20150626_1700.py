# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0007_auto_20150626_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='description',
        ),
        migrations.AddField(
            model_name='advisory',
            name='short_description',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
