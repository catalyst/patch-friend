# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0016_auto_20160308_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='architecture',
            field=models.CharField(default='amd64', help_text=b'Package architecture, which may differ from the host architecture.', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customer',
            name='name',
            field=models.CharField(help_text=b'Name of customer.', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='architecture',
            field=models.CharField(help_text=b'Machine architecture.', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_fingerprint',
            field=models.CharField(help_text=b"This host's fingerprint in hostinfo, if this host was created from hostinfo data.", max_length=200, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='hostinfo_id',
            field=models.IntegerField(help_text=b"This host's ID in hostinfo, if this host was created from hostinfo data.", null=True, verbose_name=b'Hostinfo ID'),
        ),
        migrations.AlterField(
            model_name='host',
            name='name',
            field=models.CharField(help_text=b'A name to refer to the host, usually the hostname.', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='release',
            field=models.CharField(help_text=b'Operating system release.', max_length=200),
        ),
        migrations.AlterField(
            model_name='host',
            name='status',
            field=models.CharField(help_text=b'Whether the host exists or not.', max_length=32, choices=[(b'present', b'Present'), (b'absent', b'Absent')]),
        ),
        migrations.AlterField(
            model_name='host',
            name='tags',
            field=models.ManyToManyField(help_text=b'Tags associated with this host.', to='hosts.Tag'),
        ),
        migrations.AlterField(
            model_name='host',
            name='updated',
            field=models.DateTimeField(help_text=b'When this status was discovered.', auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='key',
            field=models.CharField(help_text=b"Attribute's key.", max_length=200),
        ),
        migrations.AlterField(
            model_name='hostimportedattribute',
            name='value',
            field=models.CharField(help_text=b"Attribute's value.", max_length=200),
        ),
        migrations.AlterField(
            model_name='package',
            name='name',
            field=models.CharField(help_text=b"Name of package from the operating system's package manager.", max_length=200),
        ),
        migrations.AlterField(
            model_name='package',
            name='status',
            field=models.CharField(help_text=b'Whether the package is installed.', max_length=32, choices=[(b'present', b'Installed'), (b'absent', b'Removed')]),
        ),
        migrations.AlterField(
            model_name='package',
            name='version',
            field=models.CharField(help_text=b"The package manager's version for this package.", max_length=200),
        ),
    ]
