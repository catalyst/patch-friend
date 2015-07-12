# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0011_auto_20150702_1022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('customer', models.ForeignKey(to='hosts.Customer')),
            ],
        ),
        migrations.AlterField(
            model_name='hoststatus',
            name='status',
            field=models.CharField(max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
        ),
        migrations.AlterField(
            model_name='packagestatus',
            name='status',
            field=models.CharField(max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
        ),
    ]
