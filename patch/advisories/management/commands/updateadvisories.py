from datetime import datetime
import bz2
import json
import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from dateutil.parser import parse as dateutil_parse
import deb822
import pytz
import requests
import svn.remote

from advisories.models import *

class DebianFeed(object):
    """
    Syncs additions to the official DSA list in to the local database, as well as retrieving and parsing metadata about each one.
    """

    def __init__(self, secure_testing_url=None, cache_location=None, releases=None, architectures=None, snapshot_url=None, security_apt_url=None):
        self.secure_testing_url = secure_testing_url or "svn://anonscm.debian.org/svn/secure-testing"
        self.client = svn.remote.RemoteClient(self.secure_testing_url)
        self.cache_location = cache_location or "%s/advisory_cache/dsa" % settings.BASE_DIR
        self.releases = releases or (
            'wheezy',
            'jessie',
        )
        self.architectures = architectures or (
            'i386',
            'amd64',
            'all',
        )
        self.snapshot_url = snapshot_url or "http://snapshot.debian.org"
        self.security_apt_url = security_apt_url or "http://security.debian.org/debian-security"

    def _update_svn_repository(self):
        """
        Update the local cache of the DSA list.
        """

        try:
            os.makedirs(self.cache_location)
        except:
            pass

        try:
            dsa_list = self.client.cat('data/DSA/list')
            with open('%s/list' % self.cache_location, 'w') as dsa_list_file:
                dsa_list_file.write(dsa_list)
        except ValueError:
            raise Exception("unable to retrieve data from SVN")
        except:
            raise Exception("unknown error updating DSA list cache file")

    def _parse_svn_advisories(self):
        """
        Parse the local cache of the DSA list.
        """

        dsas = {}
        with open('%s/list' % self.cache_location) as dsa_list_file:
            dsa = ''
            packages = {}
            for line in dsa_list_file:

                # minimal state machine follows
                if line.startswith('['): # start of the DSA
                    if dsa != '' and len(packages) > 0: # at least one complete DSA parsed
                        dsas[dsa] = {
                            'packages': packages,
                            'description': description,
                            'issued': issued,
                        }
                    issued = pytz.utc.localize(dateutil_parse(line.split('] ')[0].strip('[')))
                    dsa = line.split('] ')[-1].split()[0] # upstream ID of DSA
                    description = line.split(' - ')[-1].strip() if ' - ' in line else '' # description if it exists, otherwise empty
                    packages = {}
                elif line.startswith('\t['): # source package name for a particular release

                    if '<' in line: # package has some tags
                        tags = [tag.strip('<>') for tag in line.split() if tag.startswith('<') and tag.endswith('>')]
                    else:
                        tags = []

                    if 'not-affected' in tags: # ignore package
                        continue

                    release = line.split()[0].strip("\t[] ")
                    if release not in self.releases: # no point in looking for unsupported releases
                        continue

                    if 'unfixed' in tags or 'end-of-life' in tags:
                        version = '0' # unsafe at any speed
                    else:
                        version = line.split()[3]

                    source_package = line.split()[2]
                    if source_package not in packages:
                        packages[source_package] = {}
                    packages[source_package][release] = version
        return dsas

    @transaction.atomic
    def update_local_database(self):
        """
        Update the local repository, parse it and add any new advisories to the local database.
        """
        print "  Updating security repository data...",

        release_metadata = {}
        source_packages = {}

        # grab the release metadata from the repository
        for release_name in self.releases:
            release_metadata[release_name] = deb822.Release(requests.get("%s/dists/%s/updates/Release" % (self.security_apt_url, release_name)).text)

        # grab the binary package metadata for the desired architectures
        for release_name, release_metadatum in release_metadata.iteritems():
            for component in release_metadatum['Components'].split():
                for architecture in [architecture for architecture in release_metadatum['Architectures'].split() if architecture in self.architectures]:
                    packages_url = "%s/dists/%s/%s/binary-%s/Packages.bz2" % (self.security_apt_url, release_name, component, architecture)
                    packages = deb822.Deb822.iter_paragraphs(bz2.decompress(requests.get(packages_url).content))
                    for binary_package in packages:
                        source_field = binary_package.get('Source', binary_package['Package']).split()
                        source_package_name = source_field[0]

                        try:
                            source_package_version = source_field[1].strip('()')
                        except:
                            source_package_version = binary_package['Version']

                        source_package_key = (release_name, source_package_name, source_package_version)

                        if source_package_key not in source_packages:
                            source_packages[source_package_key] = {}

                        if binary_package['Package'] not in source_packages[source_package_key]:
                            source_packages[source_package_key][binary_package['Package']] = {}

                        source_packages[source_package_key][binary_package['Package']][architecture] = binary_package['Version']

        print "OK"
        print "  Updating security-tracker data...",

        self._update_svn_repository()
        svn_advisories = self._parse_svn_advisories()
        print "OK"

        # make a set of the advisory IDs which exist on disk but not in the database
        new_advisories = set(svn_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.filter(source='debian')])

        print "  Found %i new DSAs to download" % len(new_advisories)

        for advisory in new_advisories:
            print "    Downloading %s..." % advisory,
            search_packages = set()
            description = svn_advisories[advisory]['description']
            description = description[0].upper() + description[1:]

            db_advisory = Advisory(upstream_id=advisory, source="debian", issued=svn_advisories[advisory]['issued'], short_description=description)
            db_advisory.save()
            for package, versions in svn_advisories[advisory]['packages'].iteritems():
                for release, version in versions.iteritems():
                    # make the source package object
                    db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=version)
                    db_srcpackage.save()
                    search_packages.add(package)
                    search_packages.add(version)

                    # attempt by convoluted means to get the binary packages for that source package
                    try:
                        if (release, package, version) in source_packages: # package is current so in the repo
                            for binary_package_name, binary_package_architectures in source_packages[(release, package, version)].iteritems():
                                for architecture in binary_package_architectures:
                                    db_binpackage = BinaryPackage(source_package=db_srcpackage, advisory=db_advisory, package=binary_package_name, release=release, safe_version=version, architecture=architecture)
                                    db_binpackage.save()
                                    search_packages.add(binary_package_name)
                                    search_packages.add(version)
                        else: # package is not latest in the repo, hopefully it's on snapshots.d.o
                            snapshot_url = "%s/mr/package/%s/%s/allfiles" % (self.snapshot_url, package, version)
                            snapshot_response = requests.get(snapshot_url)
                            snapshot_data = json.loads(snapshot_response.text)

                            if snapshot_data['version'] != version:
                                raise Exception("snapshots.d.o returned non-matching result")

                            for snapshot_binary in snapshot_data['result']['binaries']:
                                snapshot_binary_architectures = [file['architecture'] for file in snapshot_binary['files'] if file['architecture'] in self.architectures]
                                for architecture in snapshot_binary_architectures:
                                    db_binpackage = BinaryPackage(source_package=db_srcpackage, advisory=db_advisory, package=snapshot_binary['name'], release=release, safe_version=snapshot_binary['version'], architecture=architecture)
                                    db_binpackage.save()
                                    search_packages.add(snapshot_binary['name'])
                                    search_packages.add(snapshot_binary['version'])

                        db_advisory.search_keywords = " ".join(search_packages)
                        db_advisory.save()

                        print "OK"
                    except:
                        print "could not get binary packages for %s/%s, assuming there are none" % (release, package)

class UbuntuFeed(object):
    """
    Syncs the latest additions to the USN JSON file in to the local database.
    """

    def __init__(self, usn_url=None, cache_location=None, releases=None, architectures=None):
        self.usn_url = usn_url or 'https://usn.ubuntu.com/usn-db/database.json.bz2'
        self.cache_location = cache_location or '%s/advisory_cache/usn' % settings.BASE_DIR
        self.releases = releases or (
            'precise',
            'trusty',
        )
        self.architectures = architectures or (
            'i386',
            'amd64',
            'all',
        )

    def _update_json_advisories(self):
        """
        Download and decompress the latest USN data from Ubuntu.
        """

        response = requests.get(self.usn_url, stream=True) # the USN list is a bzip'd JSON file of all the current advisories for all supported releases
        bytes_downloaded = 0
        with open("%s/incoming-database.json.bz2" % self.cache_location, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    bytes_downloaded += len(chunk)

        if bytes_downloaded < 1500: # sanity check
            raise Exception("could not download USN feed")
        else:
            try:
                # un-bzip the file using the bz2 library and atomically replace the existing one if this succeeds
                with open("%s/incoming-database.json" % self.cache_location, 'wb') as decompressed, bz2.BZ2File("%s/incoming-database.json.bz2" % self.cache_location, 'rb') as compressed:
                    for data in iter(lambda : compressed.read(100 * 1024), b''):
                        decompressed.write(data)
                os.rename("%s/incoming-database.json" % self.cache_location, "%s/database.json" % self.cache_location)
            except:
                raise Exception("could not decompress USN feed")

    def _parse_json_advisories(self):
        """
        Produce a dictionary representing USN data from the cache file.
        """

        with open("%s/database.json" % self.cache_location) as usn_list_file:
            return json.loads(usn_list_file.read())

    @transaction.atomic
    def update_local_database(self):
        """
        Retrieve the latest JSON data, parse it and add any new advisories to the local database.
        """
        print "  Downloading JSON data..."
        self._update_json_advisories()
        json_advisories = self._parse_json_advisories()
        new_advisories = set(json_advisories) - set(['-'.join(advisory.upstream_id.split('-')[1:]) for advisory in Advisory.objects.filter(source='ubuntu')])

        print "  Found %i new USNs to process" % len(new_advisories)

        for advisory in new_advisories:
            print "    Processing USN %s..." % advisory,

            search_packages = set()

            try:
                advisory_data = json_advisories[advisory]
                db_advisory = Advisory(
                    upstream_id="USN-%s" % advisory,
                    source="ubuntu",
                    issued=datetime.utcfromtimestamp(advisory_data['timestamp']).replace(tzinfo=pytz.utc),
                    description=advisory_data.get('description', None),
                    action=advisory_data.get('action', None),
                    short_description=advisory_data.get('isummary', None)
                )
                db_advisory.save()
                for release, release_data in {release:release_data for release, release_data in json_advisories[advisory]['releases'].iteritems() if release in self.releases}.iteritems():
                    for package, package_data in release_data['sources'].items():
                        db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=package_data['version'])
                        db_srcpackage.save()
                        search_packages.add(package)
                        search_packages.add(package_data['version'])
                    for architecture in [architecture for architecture in release_data['archs'].keys() if architecture in self.architectures]:
                        for url in release_data['archs'][architecture]['urls'].keys():
                            package_filename = url.split('/')[-1]
                            if not package_filename.endswith('.deb'):
                                continue
                            binary_package_name = package_filename.split('_')[0]
                            binary_package_version = package_filename.split('_')[1]
                            db_binpackage = BinaryPackage(advisory=db_advisory, package=binary_package_name, release=release, safe_version=binary_package_version, architecture=architecture)
                            db_binpackage.save()
                            search_packages.add(binary_package_name)
                            search_packages.add(binary_package_version)
                db_advisory.search_keywords = " ".join(search_packages)
                db_advisory.save()
            except:
                print "Error"
                raise
            else:
                print "OK"

class Command(BaseCommand):
    help = 'Update all sources of advisories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating DSAs..."))
        feed = DebianFeed()
        feed.update_local_database()
        self.stdout.write(self.style.MIGRATE_HEADING("Updating USNs..."))
        feed = UbuntuFeed()
        feed.update_local_database()
