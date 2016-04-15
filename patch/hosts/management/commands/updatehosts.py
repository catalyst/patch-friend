"""
Commands to perform host discovery and package discovery runs. Presently only supporting hostinfo.

This file is a work-in-progress. Ideally this would be re-factored out in to a "hostinfo" plugin, to make room for mcollective and
native plugins later.
"""

import cProfile
import json

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone

import requests

from hosts.models import *

class HostinfoClient(object):

    def __init__(self, hostinfo_base_url=None):
        self.hostinfo_base_url = hostinfo_base_url or 'http://hostinfo/'

    def all_hosts_and_packages(self):
        return json.loads(requests.get("%s/cgi-bin/hosts-and-packages.pl" % self.hostinfo_base_url).content)

class Command(BaseCommand):
    help = 'Update all sources of hosts and packages'

    @transaction.atomic
    def _update_hostinfo_hosts(self):

        default_customer, created = Customer.objects.get_or_create(name='Catalyst')
        if created:
            default_customer.save()

        self.stdout.write("  Wrangling all host data (this will take a minute or two)... ", ending='')

        all_database_hosts = Host.objects.filter(source='hostinfo')
        all_hostinfo_hosts = self.hostinfo_client.all_hosts_and_packages()

        all_database_fingerprints = set([host.hostinfo_fingerprint for host in all_database_hosts])
        all_hostinfo_fingerprints = set([host['metadata']['fingerprint'] for hostname, host in all_hostinfo_hosts.iteritems()])

        new_hosts = all_hostinfo_fingerprints - all_database_fingerprints
        hosts_to_remove = all_database_fingerprints - all_hostinfo_fingerprints

        self.stdout.write("OK")

        self.stdout.write("  %i hosts found (%i new)" % (len(all_hostinfo_fingerprints), len(new_hosts)))

        for hostname, host_data in all_hostinfo_hosts.iteritems():
            self.stdout.write("      updating %s..." % hostname, ending='')
            db_host, db_host_created = Host.objects.get_or_create(hostinfo_fingerprint=host_data['metadata']['fingerprint'], defaults={'hostinfo_id': host_data['metadata']['hostid'], 'customer': default_customer, 'name': hostname})

            if db_host_created:
                tags = []
                customer = None
                for attribute in host_data['machineinfo']:
                    db_importedattributes, db_importedattributes_created = HostImportedAttribute.objects.get_or_create(host=db_host, key=attribute['key'], value=attribute['value'])

                    if attribute['key'] == 'CLIENT':
                        value = attribute['value'].strip()
                        if value:
                            customer = value

                    if attribute['key'] == 'PATCHING' or attribute['key'] == 'ROLE':
                        value = attribute['value'].strip()
                        if value:
                            tags.append(attribute['value'])

                if customer:
                    db_customer, db_customer_created = Customer.objects.get_or_create(name=customer)
                    db_host.customer = db_customer
                else:
                    db_customer = default_customer

                if tags:
                    for tag in tags:
                        db_tag, db_tag_created = Tag.objects.get_or_create(name=tag, customer=db_customer)
                        db_host.tags.add(db_tag)

            try:
                release = host_data['metadata']['release'].split(':')[1]
            except:
                release = ''

            try:
                architecture = host_data['metadata']['hardware'].strip()
                if architecture:
                    architecture = architecture.replace('i686','i386')
                    architecture = architecture.replace('x86_64','amd64')
            except:
                architecture = ''

            db_host.release = release
            db_host.architecture = architecture
            db_host.source = 'hostinfo'
            db_host.save()

            Package.objects.filter(host__pk=db_host.pk).delete()
            pkgs = []

            for package in host_data['packages']:
                # only 'ii' packages are imported
                if package['status'] != 'ii':
                    continue

                try:
                    package_architecture = package['name'].strip().split(':')[1]
                    package_name = package['name'].strip().split(':')[0]
                except:
                    package_architecture = architecture
                    package_name = package['name']

                pkgs.append(Package(name=package_name, version=package['version'], host=db_host, architecture=package_architecture))

            Package.objects.bulk_create(pkgs)
            self.stdout.write("Done")

        self.stdout.write("  %i removed hosts" % len(hosts_to_remove))
        Host.objects.filter(hostinfo_fingerprint__in=hosts_to_remove).delete()

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        self.hostinfo_client = HostinfoClient()

        self._update_hostinfo_hosts()
