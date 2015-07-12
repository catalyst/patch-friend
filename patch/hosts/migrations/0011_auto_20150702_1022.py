# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0010_auto_20150701_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='hoststatus',
            name='release',
            field=models.CharField(default='', max_length=32, choices=[(b'squeeze', b'Debian Squeeze'), (b'wheezy', b'Debian Wheezy'), (b'jessie', b'Debian Jessie'), (b'precise', b'Ubuntu Precise'), (b'trusty', b'Ubuntu Trusty')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_id',
            field=models.IntegerField(null=True, verbose_name=b'Hostinfo ID'),
        ),
    ]
