# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0008_auto_20150630_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostImportedAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.TextField(max_length=200)),
                ('value', models.TextField(max_length=200)),
                ('host', models.ForeignKey(to='hosts.Host')),
            ],
        ),
    ]
