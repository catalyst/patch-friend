# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0004_auto_20150626_1607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='release',
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='release',
            field=models.CharField(max_length=32, choices=[(b'squeeze', b'squeeze'), (b'wheezy', b'wheezy'), (b'jessie', b'jessie'), (b'precise', b'precise'), (b'trusty', b'trusty')]),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='release',
            field=models.CharField(max_length=32, choices=[(b'squeeze', b'squeeze'), (b'wheezy', b'wheezy'), (b'jessie', b'jessie'), (b'precise', b'precise'), (b'trusty', b'trusty')]),
        ),
    ]
