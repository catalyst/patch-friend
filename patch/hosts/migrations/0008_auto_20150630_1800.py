# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0007_auto_20150630_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PackageDiscoveryRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=32, choices=[(b'hostinfo', b'hostinfo')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('host', models.ForeignKey(to='hosts.Host')),
            ],
        ),
        migrations.CreateModel(
            name='PackageStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=32, choices=[(b'present', b'present'), (b'absent', b'absent')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('version', models.CharField(max_length=200)),
                ('discovery_run', models.ForeignKey(to='hosts.PackageDiscoveryRun')),
                ('package', models.ForeignKey(to='hosts.Package')),
            ],
            options={
                'verbose_name_plural': 'package statuses',
            },
        ),
        migrations.AddField(
            model_name='package',
            name='current_status',
            field=models.ForeignKey(related_name='+', to='hosts.PackageStatus', null=True),
        ),
        migrations.AddField(
            model_name='package',
            name='host',
            field=models.ForeignKey(to='hosts.Host'),
        ),
    ]
