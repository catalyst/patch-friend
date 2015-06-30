# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('hostinfo_fingerprint', models.CharField(max_length=200)),
                ('customer', models.ForeignKey(to='hosts.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='HostDiscoveryRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=32, choices=[(b'hostinfo', b'hostinfo')])),
                ('started', models.DateTimeField()),
                ('finished', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=32, choices=[(b'present', b'present'), (b'absent', b'absent')])),
                ('discovery_run', models.ForeignKey(to='hosts.HostDiscoveryRun')),
                ('host', models.ForeignKey(to='hosts.Host')),
            ],
        ),
    ]
