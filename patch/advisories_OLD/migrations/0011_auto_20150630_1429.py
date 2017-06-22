# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0010_binarypackage_safe_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisory',
            name='source',
            field=models.CharField(max_length=32, choices=[(b'ubuntu', b'Ubuntu'), (b'debian', b'Debian')]),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='source_package',
            field=models.ForeignKey(to='advisories.SourcePackage', null=True),
        ),
    ]
