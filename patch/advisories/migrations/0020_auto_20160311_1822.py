# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisories', '0019_auto_20160311_1537'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisory',
            name='search_packages',
        ),
        migrations.AddField(
            model_name='advisory',
            name='search_keywords',
            field=models.TextField(help_text=b'Space separated list of keywords used to speed up search', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='binarypackage',
            name='release',
            field=models.CharField(help_text=b'Specific release to which this package belongs', max_length=32, choices=[(b'squeeze', b'Debian Squeeze 6.0'), (b'wheezy', b'Debian Wheezy 7.0'), (b'jessie', b'Debian Jessie 8.0'), (b'precise', b'Ubuntu Precise LTS 12.04'), (b'trusty', b'Ubuntu Trusty LTS 14.04')]),
        ),
        migrations.AlterField(
            model_name='sourcepackage',
            name='release',
            field=models.CharField(help_text=b'Specific release to which this package belongs', max_length=32, choices=[(b'squeeze', b'Debian Squeeze 6.0'), (b'wheezy', b'Debian Wheezy 7.0'), (b'jessie', b'Debian Jessie 8.0'), (b'precise', b'Ubuntu Precise LTS 12.04'), (b'trusty', b'Ubuntu Trusty LTS 14.04')]),
        ),
    ]
