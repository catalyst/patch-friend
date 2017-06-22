# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0002_auto_20150626_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisory',
            name='release',
            field=models.TextField(default='jessie', choices=[(b'squeeze', b'squeeze'), (b'wheezy', b'wheezy'), (b'jessie', b'jessie'), (b'precise', b'precise'), (b'trusty', b'trusty')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisory',
            name='source',
            field=models.TextField(default='debian', choices=[(b'ubuntu', b'ubuntu'), (b'debian', b'debian')]),
            preserve_default=False,
        ),
    ]
