# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0003_auto_20150626_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisory',
            name='release',
            field=models.CharField(max_length=32, choices=[(b'squeeze', b'squeeze'), (b'wheezy', b'wheezy'), (b'jessie', b'jessie'), (b'precise', b'precise'), (b'trusty', b'trusty')]),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='source',
            field=models.CharField(max_length=32, choices=[(b'ubuntu', b'ubuntu'), (b'debian', b'debian')]),
        ),
    ]
