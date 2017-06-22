# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import advisories.models


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0021_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binarypackage',
            name='safe_version',
            field=advisories.models.DebversionField(help_text=b"Package version that is to be considered 'safe' at the issue of this advisory", max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='safe_version',
            field=advisories.models.DebversionField(help_text=b"Package version that is to be considered 'safe' at the issue of this advisory", max_length=200),
        ),
    ]
