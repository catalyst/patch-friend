# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-13 01:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of customer.', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A name to refer to the host, usually the hostname.', max_length=200)),
                ('hostinfo_fingerprint', models.CharField(help_text="This host's fingerprint in hostinfo, if this host was created from hostinfo data.", max_length=200, null=True, unique=True)),
                ('hostinfo_id', models.IntegerField(help_text="This host's ID in hostinfo, if this host was created from hostinfo data.", null=True, verbose_name='Hostinfo ID')),
                ('architecture', models.CharField(help_text='Machine architecture.', max_length=200)),
                ('release', models.CharField(help_text='Operating system release.', max_length=200)),
                ('updated', models.DateTimeField(auto_now_add=True, help_text='When this status was discovered.')),
                ('source', models.CharField(choices=[('hostinfo', 'hostinfo')], help_text="Source of this host's data.", max_length=32)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosts.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='HostImportedAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text="Attribute's key.", max_length=200)),
                ('value', models.CharField(help_text="Attribute's value.", max_length=200)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosts.Host')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Name of package from the operating system's package manager.", max_length=200)),
                ('version', models.CharField(help_text="The package manager's version for this package.", max_length=200)),
                ('architecture', models.CharField(help_text='Package architecture, which may differ from the host architecture.', max_length=200)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosts.Host')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosts.Customer')),
            ],
        ),
        migrations.AddField(
            model_name='host',
            name='tags',
            field=models.ManyToManyField(help_text='Tags associated with this host.', to='hosts.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('name', 'customer')]),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together=set([('name', 'host', 'architecture')]),
        ),
        migrations.AlterUniqueTogether(
            name='hostimportedattribute',
            unique_together=set([('host', 'key')]),
        ),
    ]
