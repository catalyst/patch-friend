# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0011_auto_20150630_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisory',
            name='action',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='advisory',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
