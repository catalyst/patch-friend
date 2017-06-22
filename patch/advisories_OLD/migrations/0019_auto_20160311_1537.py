# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0018_auto_20160311_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binarypackage',
            name='source_package',
            field=models.ForeignKey(blank=True, to='advisories.SourcePackage', help_text=b'If set, the source package from which this binary package was generated', null=True),
        ),
    ]
