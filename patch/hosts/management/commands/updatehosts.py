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

        print "  Wrangling all host data (this will take a minute or two)... ",

        all_database_hosts = Host.objects.filter(source='hostinfo')
        all_hostinfo_hosts = self.hostinfo_client.all_hosts_and_packages()

        all_database_fingerprints = set([host.hostinfo_fingerprint for host in all_database_hosts])
        all_hostinfo_fingerprints = set([host['metadata']['fingerprint'] for hostname, host in all_hostinfo_hosts.iteritems()])

        new_hosts = all_hostinfo_fingerprints - all_database_fingerprints
        hosts_to_remove = all_database_fingerprints - all_hostinfo_fingerprints

        print "OK"

        print "  %i hosts found (%i new)" % (len(all_hostinfo_fingerprints), len(new_hosts))

        for hostname, host_data in all_hostinfo_hosts.iteritems():
            print "      updating %s..." % hostname,
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

            db_host.status = 'present'
            db_host.release = release
            db_host.architecture = architecture
            db_host.source = 'hostinfo'
            db_host.save()

            Package.objects.filter(host__pk=db_host.pk).delete()
            pkgs = []

            for package in host_data['packages']:
                if package['status'] == 'ii':
                    status = 'present'
                else:
                    status = 'absent'

                try:
                    package_architecture = package['name'].strip().split(':')[1]
                    package_name = package['name'].strip().split(':')[0]
                except:
                    package_architecture = architecture
                    package_name = package['name']

                pkgs.append(Package(name=package_name, version=package['version'], status=status, host=db_host, architecture=package_architecture))

            Package.objects.bulk_create(pkgs)
            print "Done"


        print "  %i removed hosts" % len(hosts_to_remove)

        for fingerprint in hosts_to_remove:
            db_host = Host.objects.get(hostinfo_fingerprint=fingerprint)
            print "      updating %s..." % db_host.name,
            db_host.status = 'absent'
            db_host.save()
            print "Done"


    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        self.hostinfo_client = HostinfoClient()

        self._update_hostinfo_hosts()

        return

        self.stdout.write(self.style.MIGRATE_HEADING("Updating packages for hosts..."))

        with transaction.atomic():
            host_statuses = Paginator(HostDiscoveryRun.objects.filter(source='hostinfo').latest('created').hoststatus_set.filter(status='present'), 20)
            for page in host_statuses.page_range:
                print "    interrogating hostinfo for 20 hosts..."

                host_ids = [host_status.host.hostinfo_id for host_status in host_statuses.page(page)]

                for host_id in host_ids:
                    host_package_data = self.hostinfo_client.packages_for_host(host_id)

# for host_id, packages in host_package_data.iteritems():
#     host = Host.objects.get(hostinfo_id=host_id)
#     print "      updating %s..." % host.name,

#     self._update_packages_for_host(host, packages)
#     print "Done"


