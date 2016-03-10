# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0015_auto_20160302_1416'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hoststatus',
            name='discovery_run',
        ),
        migrations.RemoveField(
            model_name='hoststatus',
            name='host',
        ),
        migrations.RemoveField(
            model_name='packagediscoveryrun',
            name='host',
        ),
        migrations.AlterUniqueTogether(
            name='packagestatus',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='packagestatus',
            name='discovery_run',
        ),
        migrations.RemoveField(
            model_name='packagestatus',
            name='package',
        ),
        migrations.RemoveField(
            model_name='host',
            name='current_status',
        ),
        migrations.RemoveField(
            model_name='package',
            name='current_status',
        ),
        migrations.AddField(
            model_name='host',
            name='architecture',
            field=models.CharField(default='amd64', help_text=b'Machine architecture', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='host',
            name='release',
            field=models.CharField(default='trusty', help_text=b'Operating system release', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='host',
            name='status',
            field=models.CharField(default='present', help_text=b'Whether the host exists or not', max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='host',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 8, 4, 19, 6, 395958, tzinfo=utc), help_text=b'When this status was discovered', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='package',
            name='status',
            field=models.CharField(default='present', help_text=b'Whether the package is installed', max_length=32, choices=[(b'present', b'Installed'), (b'absent', b'Removed')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='package',
            name='version',
            field=models.CharField(default='0', help_text=b"The package manager's version for this package", max_length=200),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='HostDiscoveryRun',
        ),
        migrations.DeleteModel(
            name='HostStatus',
        ),
        migrations.DeleteModel(
            name='PackageDiscoveryRun',
        ),
        migrations.DeleteModel(
            name='PackageStatus',
        ),
    ]
