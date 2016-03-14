# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0017_auto_20160309_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='source',
            field=models.CharField(default='hostinfo', help_text=b"Source of this host's data.", max_length=32, choices=[(b'hostinfo', b'hostinfo')]),
            preserve_default=False,
        ),
    ]
