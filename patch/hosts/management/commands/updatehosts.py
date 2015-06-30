import json

import requests

from hosts.models import *

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

class HostinfoClient(object):
    
    def __init__(self, hostinfo_base_url=None):
        self.hostinfo_base_url = hostinfo_base_url or 'http://hostinfo/'

    def all_hosts(self):
        return json.loads(requests.get("%s/cgi-bin/hosts.pl" % self.hostinfo_base_url).content).get('hosts', [])

    def packages_for_host(self, host_id):
        return json.loads(requests.get("%s/cgi-bin/host-related.pl?&relationship=packages&hostid=%i" % (self.hostinfo_base_url, host_id)).content)

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
            db_host, db_host_created = Host.objects.get_or_create(hostinfo_fingerprint=fingerprint, defaults={'hostinfo_id': host_data['hostid'], 'customer': Customer(1), 'name': host_data['hostname']})
            db_hoststatus = HostStatus(host=db_host, discovery_run=db_discoveryrun, status='present')
            db_hoststatus.save()
            db_host.current_status = db_hoststatus
            db_host.save()            

        removed_hosts = set(all_database_fingerprints) - set(all_hostinfo_fingerprints)
        print "  %i removed hosts" % len(removed_hosts)

        for fingerprint in removed_hosts:
            db_host = Host.objects.get(hostinfo_fingerprint=fingerprint)
            db_hoststatus = HostStatus(host=db_host, discovery_run=db_discoveryrun, status='absent')
            db_hoststatus.save()
            db_host.current_status = db_hoststatus
            db_host.save()

    @transaction.atomic
    def _update_packages_for_host(self, host):
        try:
            current_database_packages = host.packagediscoveryrun_set.latest('created').package_set.filter(status='present')
        except:
            current_database_packages = []

        db_discoveryrun = PackageDiscoveryRun(source="hostinfo", host=host)
        db_discoveryrun.save()

        hostinfo_packages = self.hostinfo_client.packages_for_host(host.hostinfo_id)
        for package in hostinfo_packages:
            db_package, db_package_created = Package.objects.get_or_create(name=package['package'], host=host)
            db_packagestatus = PackageStatus(package=db_package, discovery_run=db_discoveryrun, status="present", version=package['version'])
            db_packagestatus.save()
            db_package.current_status = db_packagestatus
            db_package.save()

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        self.hostinfo_client = HostinfoClient()

        self._update_hostinfo_hosts()
        self._update_packages_for_host(Host.objects.all()[:1][0])

