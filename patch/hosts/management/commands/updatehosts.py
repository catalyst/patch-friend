"""
Commands to perform host discovery and package discovery runs. Presently only supporting hostinfo.

This file is a work-in-progress. Ideally this would be re-factored out in to a "hostinfo" plugin, to make room for mcollective and
native plugins later.
"""

import cProfile
import json

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

import requests
import logging
from hashlib import sha256

from hosts.models import *

logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.DEBUG)

class HostinfoClient(object):

    def __init__(self, hostinfo_base_url=None):
        self.hostinfo_base_url = hostinfo_base_url or 'http://hostinfo/'

    def all_hosts_and_packages(self):
        # return json.loads(requests.get("%s/cgi-bin/hosts-and-packages.pl" % self.hostinfo_base_url).content)
        return requests.get("%s/cgi-bin/hosts-and-packages.pl" % self.hostinfo_base_url).json()

class Command(BaseCommand):
    help = 'Update all sources of hosts and packages'

    @transaction.atomic
    def _update_hostinfo_hosts(self):

        default_customer, created = Customer.objects.get_or_create(name='catalyst')
        if created:
            default_customer.save()

        self.stdout.write("  Wrangling all host data (this will take a minute or two)... ", ending='')

        all_database_hosts = Host.objects.filter(source='hostinfo')
        # print('all_database_hosts', all_database_hosts)
        # logging.info('all_database_hosts done')
        all_hostinfo_hosts = self.hostinfo_client.all_hosts_and_packages()
        # print('all_hostinfo_hosts', all_hostinfo_hosts)
        # logging.info('all_hostinfo_hosts done')


        all_database_fingerprints = {host.hostinfo_fingerprint for host in all_database_hosts}
        all_hostinfo_fingerprints = {host['metadata']['fingerprint'] for hostname, host in all_hostinfo_hosts.items()}


        new_hosts = all_hostinfo_fingerprints - all_database_fingerprints
        logging.debug('New hosts: ' + str(new_hosts))
        hosts_to_remove = all_database_fingerprints - all_hostinfo_fingerprints
        logging.debug('Hosts to remove: ' + str(hosts_to_remove))

        self.stdout.write("OK")

        self.stdout.write("  %i hosts found (%i new)" % (len(all_hostinfo_fingerprints), len(new_hosts)))

        for hostname, host_data in all_hostinfo_hosts.items():

            hostinfo_host_hash = sha256(json.dumps(sorted(host_data['machineinfo'], key=sorted), sort_keys=True).encode('utf-8')).hexdigest()

            self.stdout.write("      updating %s..." % hostname, ending='')
            db_host, db_host_created = Host.objects.get_or_create(hostinfo_fingerprint=host_data['metadata']['fingerprint'], defaults={'hostinfo_id': host_data['metadata']['hostid'], 'customer': default_customer, 'name': hostname})

            if db_host_created or (hostinfo_host_hash != db_host.host_hash):
                tags = []
                customer = None
                HostImportedAttribute.objects.filter(host=db_host).delete()  # Clear any previous attributes that there might have been
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
                    db_customer, db_customer_created = Customer.objects.get_or_create(name=customer.lower())
                    db_host.customer = db_customer
                else:
                    db_customer = default_customer

                if tags:
                    for tag in tags:
                        db_tag, db_tag_created = Tag.objects.get_or_create(name=tag, customer=db_customer)
                        db_host.tags.add(db_tag)

                db_host.host_hash = hostinfo_host_hash
                # print('Hash is different')

            try:
                release = host_data['metadata']['release'].split(':')[1]
            except:
                logging.error(hostname + ' has no release!')
                release = ''

            try:
                architecture = host_data['metadata']['hardware'].strip()
                if architecture:
                    architecture = architecture.replace('i686','i386')
                    architecture = architecture.replace('x86_64','amd64')
            except:
                logging.error(hostname + ' has no architecture!')
                architecture = ''

            db_host.release = release
            db_host.architecture = architecture
            db_host.source = 'hostinfo'
            db_host.save()


            # Does the packages
            pkgs = []
            hostinfo_packages = set()

            logging.info("Getting packages from databse...")
            database_packages = set(Package.objects.filter(host=db_host).values_list("name", "version", "architecture"))
            # print(database_packages)

            # for every package in hostinfo host...
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

                hostinfo_packages.add((package_name, package['version'], package_architecture))


            # Any packages that are in hostinfo but not in database will be added to database
            packages_to_add = hostinfo_packages - database_packages
            # print("\n\npackages to add: ", packages_to_add, "\n")

            # Any packages that are /not/ in hostinfo but are in database have been removed, so will be deleted from database
            packages_to_remove = database_packages - hostinfo_packages
            # print("packages to remove: ", packages_to_remove, "\n")

            # Removes each package that is in packages_to_remove from the database
            for package in packages_to_remove:
                Package.objects.filter(name=package[0], version=package[1], host=db_host, architecture=package[2]).delete()

            # Adds all the package from packages_to_add into the database
            for package in packages_to_add:
                Package(name=package[0], version=package[1], host=db_host, architecture=package[2]).save()

            self.stdout.write("Done")

        self.stdout.write("  %i removed hosts" % len(hosts_to_remove))
        Host.objects.filter(hostinfo_fingerprint__in=hosts_to_remove).delete()

        # entries in advisories_cache are only valid for the hostinfo run they were generated against
        # self.stdout.write("  clearing advisories cache")
        # cache.clear()

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating hosts from hostinfo..."))
        self.hostinfo_client = HostinfoClient()

        self._update_hostinfo_hosts()
