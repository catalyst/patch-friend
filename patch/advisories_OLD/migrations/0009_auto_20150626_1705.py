# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0008_auto_20150626_1700'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='debian_id',
        ),
        migrations.AddField(
            model_name='advisory',
            name='upstream_id',
            field=models.CharField(default='', max_length=200, verbose_name=b'Upstream ID'),
            preserve_default=False,
        ),
    ]
