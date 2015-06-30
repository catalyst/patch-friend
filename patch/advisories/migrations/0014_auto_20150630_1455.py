# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0013_auto_20150630_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisory',
            name='short_description',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
