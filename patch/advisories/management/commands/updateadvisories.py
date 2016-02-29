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

    def __init__(self, secure_testing_url=None, cache_location=None, releases=None):
        self.client = pysvn.Client()
        self.secure_testing_url = secure_testing_url or 'svn://anonscm.debian.org/svn/secure-testing'
        self.cache_location = cache_location or '%s/advisory_cache/dsa' % settings.BASE_DIR
        self.releases = releases or (
            'squeeze',
            'wheezy',
            'jessie',
        )

    def _update_repository(self):
        """
        Update the local checkout of the subversion repository where the advisory lists are kept.
        """

        repo_path = "%s/svn" % self.cache_location
        number = -1
        try:
            os.makedirs(repo_path)
        except:
            pass

        # update to the latest remote revision of the SVN repo
        number = self.client.update(repo_path)[0].number

        # if the repo didn't yet exist locally, update() will have done nothing
        if number == -1 or not os.path.isfile('%s/svn/data/DSA/list' % self.cache_location):
            self.client.checkout(self.secure_testing_url, repo_path)
        else:
            return number

    def _source_package_to_binary_packages(self, source_package, release):
        """
        Grab data haphazardly from the Debian website to determine the implicated binary packages
        for a given source package.
        """

        dsc_search = re.compile('"([^"]*\.dsc)"')

        # grab the human readable package page...
        packages_page = requests.get("https://packages.debian.org/source/%s/%s" % (release, source_package))

        # find the first string inside quotes that ends with '.dsc'
        try:
            dsc_page = requests.get(dsc_search.findall(packages_page.content)[0])
        except:
            raise Exception("could not find DSC file path for %s in %s" % (source_package, release))

        # parse with deb822
        binary_packages = deb822.Dsc(dsc_page.content)['Binary'].split()
        return [package.strip(', ') for package in binary_packages]

    def _parse_svn_advisories(self):
        """
        Parse the DSA list from the local checkout of the subversion repository and return a dictionary representing the data.
        """

        dsas = {}
        with open('%s/svn/data/DSA/list' % self.cache_location) as dsa_list_file:
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
                elif line.startswith('\t[') and '<not-affected>' not in line: # source package name for a particular release
                    release = line.split()[0].strip("\t[] ")
                    if release not in self.releases: # no point in looking for unsupported releases
                        continue
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

        self._update_repository() # ensure the local repo is up to date
        svn_advisories = self._parse_svn_advisories()

        # make a set of the advisory IDs which exist on disk but not in the database
        new_advisories = set(svn_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.filter(source='debian')])

        print "  %i new DSAs to download" % len(new_advisories)

        for advisory in new_advisories:
            print "    downloading %s..." % advisory,
            db_advisory = Advisory(upstream_id=advisory, source="debian", issued=svn_advisories[advisory]['issued'], short_description=svn_advisories[advisory]['description'])
            db_advisory.save()
            for package, versions in svn_advisories[advisory]['packages'].iteritems():
                for release, version in versions.iteritems():
                    db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=version)
                    db_srcpackage.save()
                    try:
                        binary_packages = self._source_package_to_binary_packages(package, release)
                        for binary_package in binary_packages:
                            # XXX it is assumed that the binary package's version matches the source package. this is only true /most/ of the time :(
                            db_binpackage = BinaryPackage(source_package=db_srcpackage, advisory=db_advisory, package=binary_package, release=release, safe_version=version)
                            db_binpackage.save()
                    except:
                        print "(could not get binary packages for %s/%s)" % (release, package),

class UbuntuFeed(object):
    """
    Syncs the latest additions to the USN JSON file in to the local database.
    """

    def __init__(self, usn_url=None, cache_location=None, releases=None):
        self.usn_url = usn_url or 'https://usn.ubuntu.com/usn-db/database.json.bz2'
        self.cache_location = cache_location or '%s/advisory_cache/usn' % settings.BASE_DIR
        self.releases = releases or (
            'precise',
            'trusty',
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

        self._update_json_advisories()
        json_advisories = self._parse_json_advisories()
        new_advisories = set(json_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.filter(source='ubuntu')])

        print "  %i new USNs to process" % len(new_advisories)

        for advisory in new_advisories:
            print "    processing USN %s..." % advisory,

            try:
                advisory_data = json_advisories[advisory]
                db_advisory = Advisory(
                    upstream_id=advisory,
                    source="ubuntu",
                    issued=datetime.utcfromtimestamp(advisory_data['timestamp']).replace(tzinfo=pytz.utc),
                    description=advisory_data.get('description', None),
                    action=advisory_data.get('action', None),
                    short_description=advisory_data.get('isummary', None)
                )
                db_advisory.save()
                for release, release_data in json_advisories[advisory]['releases'].items():
                    for package, package_data in release_data['sources'].items():
                        db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=package_data['version'])
                        db_srcpackage.save()
                    for package, package_data in release_data['binaries'].items():
                        db_binpackage = BinaryPackage(advisory=db_advisory, package=package, release=release, safe_version=package_data['version'])
                        db_binpackage.save()
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
