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

class Command(BaseCommand):
    help = 'Update all sources of hosts and packages'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        client = HostinfoClient()

        try:
            all_database_hosts = HostDiscoveryRun.objects.filter(source='hostinfo').latest('created').hoststatus_set.filter(status='present')
        except: # XXX make check for missing HostDiscoveryRun more specific
            all_database_hosts = []

        db_discoveryrun = HostDiscoveryRun(source="hostinfo")
        db_discoveryrun.save()

        all_hostinfo_hosts = client.all_hosts()
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
