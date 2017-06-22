# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0014_auto_20150630_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='binarypackage',
            name='architecture',
            field=models.CharField(help_text=b'Machine architecture', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='action',
            field=models.TextField(help_text=b'What, if any, actions need to be taken to address the advisory', null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='description',
            field=models.TextField(help_text=b'Longer description of the advisory', null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='issued',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text=b'Date and time at which the advisory was issued'),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='reviewed_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, help_text=b'Person who locally reviewed the advisory for its overall severity (or None if the severity was determined automatically)', null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='severity',
            field=models.CharField(default=0, help_text=b'Local severity of the advisory, once it has been reviewed', max_length=32, choices=[(0, b'Undecided'), (1, b'Low'), (2, b'Standard'), (3, b'High'), (4, b'Critical')]),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='short_description',
            field=models.CharField(help_text=b'One-line description of the advisory', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='source',
            field=models.CharField(help_text=b'Vendor source of the advisory', max_length=32, choices=[(b'ubuntu', b'Ubuntu'), (b'debian', b'Debian')]),
        ),
        migrations.AlterField(
            model_name='advisory',
            name='upstream_id',
            field=models.CharField(help_text=b'The ID used by the vendor to refer to this advisory', max_length=200, verbose_name=b'Upstream ID'),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='advisory',
            field=models.ForeignKey(help_text=b'Advisory to which this package belongs', to='advisories.Advisory'),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='package',
            field=models.CharField(help_text=b'Name of binary package', max_length=200),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='release',
            field=models.CharField(help_text=b'Specific release to which this package belongs', max_length=32, choices=[(b'squeeze', b'Debian Squeeze'), (b'wheezy', b'Debian Wheezy'), (b'jessie', b'Debian Jessie'), (b'precise', b'Ubuntu Precise'), (b'trusty', b'Ubuntu Trusty')]),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='safe_version',
            field=models.CharField(help_text=b"Package version that is to be considered 'safe' at the issue of this advisory", max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='source_package',
            field=models.ForeignKey(to='advisories.SourcePackage', help_text=b'If set, the source package from which this binary package was generated', null=True),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='advisory',
            field=models.ForeignKey(help_text=b'Advisory to which this package belongs', to='advisories.Advisory'),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='package',
            field=models.CharField(help_text=b'Name of source package', max_length=200),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='release',
            field=models.CharField(help_text=b'Specific release to which this package belongs', max_length=32, choices=[(b'squeeze', b'Debian Squeeze'), (b'wheezy', b'Debian Wheezy'), (b'jessie', b'Debian Jessie'), (b'precise', b'Ubuntu Precise'), (b'trusty', b'Ubuntu Trusty')]),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='safe_version',
            field=models.CharField(help_text=b"Package version that is to be considered 'safe' at the issue of this advisory", max_length=200),
        ),
    ]
