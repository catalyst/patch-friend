# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advisory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('debian_id', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='BinaryPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('package', models.CharField(max_length=200)),
                ('release', models.CharField(max_length=200)),
                ('advisory', models.ForeignKey(to='advisories.Advisory')),
            ],
        ),
        migrations.CreateModel(
            name='SourcePackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('package', models.CharField(max_length=200)),
                ('release', models.CharField(max_length=200)),
                ('safe_version', models.CharField(max_length=200)),
                ('advisory', models.ForeignKey(to='advisories.Advisory')),
            ],
        ),
    ]
