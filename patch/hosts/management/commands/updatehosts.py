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

    def all_hosts(self):
        return json.loads(requests.get("%s/cgi-bin/hosts.pl" % self.hostinfo_base_url).content).get('hosts', [])

    def packages_for_host(self, host_id):
        return json.loads(requests.get("%s/cgi-bin/host-related.pl?&relationship=packages&hostid=%i" % (self.hostinfo_base_url, int(host_id))).content)

    def machineinfo_for_host(self, host_id):
        return json.loads(requests.get("%s/cgi-bin/host-related.pl?&relationship=cat_machineinfos&hostid=%i" % (self.hostinfo_base_url, int(host_id))).content)

class Command(BaseCommand):
    help = 'Update all sources of hosts and packages'

    @transaction.atomic
    def _update_hostinfo_hosts(self):
        try:
            all_database_hosts = HostDiscoveryRun.objects.filter(source='hostinfo').latest('created').hoststatus_set.filter(status='present')
        except: # XXX make check for missing HostDiscoveryRun more specific
            all_database_hosts = []

        db_discoveryrun = HostDiscoveryRun(source="hostinfo")
        db_discoveryrun.save()

        all_hostinfo_hosts = self.hostinfo_client.all_hosts()
        all_database_fingerprints = [host.host.hostinfo_fingerprint for host in all_database_hosts]
        all_hostinfo_fingerprints = {host['fingerprint']: host for host in all_hostinfo_hosts}

        new_hosts = set(all_hostinfo_fingerprints) - set(all_database_fingerprints)

        print "  %i hosts found (%i new)" % (len(all_hostinfo_fingerprints), len(new_hosts))

        for fingerprint, host_data in all_hostinfo_fingerprints.iteritems():
            print "      updating %s..." % host_data['hostname'],
            db_host, db_host_created = Host.objects.get_or_create(hostinfo_fingerprint=fingerprint, defaults={'hostinfo_id': host_data['hostid'], 'customer': Customer(1), 'name': host_data['hostname']})

            if db_host_created:
                tags = []
                customer = None
                for attribute in self.hostinfo_client.machineinfo_for_host(host_data['hostid']):
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
                    db_customer = Customer(1)

                if tags:
                    for tag in tags:
                        db_tag, db_tag_created = Tag.objects.get_or_create(name=tag, customer=db_customer)
                        db_host.tags.add(db_tag)

            try:
                release = host_data['release'].split(':')[1]
            except:
                release = ''

            db_hoststatus = HostStatus(host=db_host, discovery_run=db_discoveryrun, status='present', release=host_data['release'].split(':')[1])
            db_hoststatus.save()
            db_host.current_status = db_hoststatus
            db_host.save()
            print "Done"


        removed_hosts = set(all_database_fingerprints) - set(all_hostinfo_fingerprints)
        print "  %i removed hosts" % len(removed_hosts)

        for fingerprint in removed_hosts:
            db_host = Host.objects.get(hostinfo_fingerprint=fingerprint)
            print "      updating %s..." % db_host.name,
            db_hoststatus = HostStatus(host=db_host, discovery_run=db_discoveryrun, status='absent')
            db_hoststatus.save()
            db_host.current_status = db_hoststatus
            db_host.save()
            print "Done"

    def _update_packages_for_host(self, host, packages=None):
        try:
            current_database_packages = host.packagediscoveryrun_set.latest('created').package_set.filter(status='present')
        except:
            current_database_packages = []

        db_discoveryrun = PackageDiscoveryRun(source="hostinfo", host=host)
        db_discoveryrun.save()

        if not packages:
            hostinfo_packages = self.hostinfo_client.packages_for_host(host.hostinfo_id)
        else:
            hostinfo_packages = packages

        for package in hostinfo_packages:
            if package['status'] == 'ii': # installed
                status = 'present'
            else:
                status = 'absent'

            db_package, db_package_created = Package.objects.get_or_create(name=package['package'], host=host)
            db_packagestatus = PackageStatus(package=db_package, discovery_run=db_discoveryrun, status=status, version=package['version'])
            db_packagestatus.save()
            db_package.current_status = db_packagestatus
            db_package.save()

    def handle(self, *args, **options):
        #self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        self.hostinfo_client = HostinfoClient()

        #self._update_hostinfo_hosts()

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


