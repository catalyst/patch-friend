# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0014_auto_20150707_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(help_text=b'Name of customer', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='current_status',
            field=models.ForeignKey(related_name='+', to='hosts.HostStatus', help_text=b'Direct reference to the newest status for this host', null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_fingerprint',
            field=models.CharField(help_text=b"This host's fingerprint in hostinfo, if this host was created from hostinfo data", max_length=200, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_id',
            field=models.IntegerField(help_text=b"This host's ID in hostinfo, if this host was created from hostinfo data", null=True, verbose_name=b'Hostinfo ID'),
        ),
        migrations.AlterField(
            model_name='host',
            name='name',
            field=models.CharField(help_text=b'A name to refer to the host, usually the hostname', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='tags',
            field=models.ManyToManyField(help_text=b'Tags associated with this host', to='hosts.Tag'),
        ),
        migrations.AlterField(
            model_name='hostdiscoveryrun',
            name='created',
            field=models.DateTimeField(help_text=b'Time at which the run started', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='hostdiscoveryrun',
            name='source',
            field=models.CharField(help_text=b'Data source from which this run was collected', max_length=32, choices=[(b'hostinfo', b'hostinfo')]),
        ),
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='key',
            field=models.CharField(help_text=b"Attribute's key", max_length=200),
        ),
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='value',
            field=models.CharField(help_text=b"Attribute's value", max_length=200),
        ),
        migrations.AlterField(
            model_name='hoststatus',
            name='created',
            field=models.DateTimeField(help_text=b'When this status was discovered', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='hoststatus',
            name='release',
            field=models.CharField(help_text=b'The operating system release of the host', max_length=32, choices=[(b'squeeze', b'Debian Squeeze'), (b'wheezy', b'Debian Wheezy'), (b'jessie', b'Debian Jessie'), (b'precise', b'Ubuntu Precise'), (b'trusty', b'Ubuntu Trusty')]),
        ),
        migrations.AlterField(
            model_name='hoststatus',
            name='status',
            field=models.CharField(help_text=b'Set to the new status of the host if it has changed since the last run from this source', max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
        ),
        migrations.AlterField(
            model_name='package',
            name='current_status',
            field=models.ForeignKey(related_name='+', to='hosts.PackageStatus', help_text=b'Direct reference to the newest status for this package', null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='name',
            field=models.CharField(help_text=b"Name of package from the operating system's package manager", max_length=200),
        ),
        migrations.AlterField(
            model_name='packagediscoveryrun',
            name='created',
            field=models.DateTimeField(help_text=b'When this status was discovered', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='packagediscoveryrun',
            name='source',
            field=models.CharField(help_text=b'Data source from which this run was collected', max_length=32, choices=[(b'hostinfo', b'hostinfo')]),
        ),
        migrations.AlterField(
            model_name='packagestatus',
            name='created',
            field=models.DateTimeField(help_text=b'When this status was discovered', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='packagestatus',
            name='status',
            field=models.CharField(help_text=b'Set to the new status of the package if it has changed since the last run from this source', max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
        ),
        migrations.AlterField(
            model_name='packagestatus',
            name='version',
            field=models.CharField(help_text=b"The package manager's version for this package", max_length=200),
        ),
    ]
