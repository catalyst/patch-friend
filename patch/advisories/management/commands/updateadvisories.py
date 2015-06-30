import bz2
import os
import re
import json
from datetime import datetime

import deb822
import pysvn
import pytz
import requests

from dateutil.parser import parse as dateutil_parse

from django.core.management.base import BaseCommand, CommandError
from advisories.models import *
from django.conf import settings

class DebianFeed(object):

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
        repo_path = "%s/svn" % self.cache_location
        number = -1
        try:
            os.makedirs(repo_path)
        except:
            pass

        number = self.client.update(repo_path)[0].number

        if number == -1 or not os.path.isfile('%s/svn/data/DSA/list' % self.cache_location): # the repo doesn't exist yet in the cache
            self.client.checkout(self.secure_testing_url, repo_path)

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
        dsas = {}
        with open('%s/svn/data/DSA/list' % self.cache_location) as dsa_list_file:
            dsa = ''
            packages = {}
            for line in dsa_list_file:
                if line.startswith('['): # start of the DSA
                    if dsa != '' and len(packages) > 0: # at least one complete DSA parsed
                        dsas[dsa] = {
                            'packages': packages,
                            'description': description,
                            'issued': issued,
                        }
                    issued = pytz.utc.localize(dateutil_parse(line.split('] ')[0].strip('[')))
                    dsa = line.split('] ')[-1].split()[0]
                    description = line.split(' - ')[-1].strip() if ' - ' in line else ''
                    packages = {}
                elif line.startswith('\t[') and '<not-affected>' not in line: # source package name for a particular release
                    release = line.split()[0].strip("\t[] ")
                    if release not in self.releases: # no point in looking for ancient releases
                        continue
                    version = line.split()[3]
                    source_package = line.split()[2]
                    if source_package not in packages:
                        packages[source_package] = {}
                    packages[source_package][release] = version
        return dsas

    def update_local_database(self):
        self._update_repository()       
        svn_advisories = self._parse_svn_advisories()
        new_advisories = set(svn_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.filter(source='debian')])

        print "  %i new DSAs to download" % len(new_advisories)

        for advisory in new_advisories:
            print "    downloading DSA %s..." % advisory,
            db_advisory = Advisory(upstream_id=advisory, source="debian", issued=svn_advisories[advisory]['issued'], short_description=svn_advisories[advisory]['description'])
            db_advisory.save()
            for package, versions in svn_advisories[advisory]['packages'].iteritems():
                for release, version in versions.iteritems():
                    db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=version)
                    db_srcpackage.save()                    
                    try:
                        binary_packages = self._source_package_to_binary_packages(package, release)
                        for binary_package in binary_packages:
                            db_binpackage = BinaryPackage(source_package=db_srcpackage, advisory=db_advisory, package=binary_package, release=release)
                            db_binpackage.save()
                    except:
                        print "Error (could not get binary packages for %s/%s)" % (release, package)
                    else:
                        print "OK"

class UbuntuFeed(object):

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

        response = requests.get(self.usn_url, stream=True)
        bytes_downloaded = 0
        with open("%s/incoming-database.json.bz2" % self.cache_location, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)
                    f.flush()
                    bytes_downloaded += len(chunk)

        if bytes_downloaded < 1500:
            raise Exception("could not download USN feed")
        else:
            try:
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

    def update_local_database(self):
        self._update_json_advisories()
        json_advisories = self._parse_json_advisories()
        new_advisories = set(json_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.filter(source='ubuntu')])

        print "  %i new USNs to process" % len(new_advisories)

        for advisory in new_advisories:
            print "    processing USN %s..." % advisory,

            try:
                db_advisory = Advisory(upstream_id=advisory, source="ubuntu", issued=datetime.utcfromtimestamp(json_advisories[advisory]['timestamp']).replace(tzinfo=pytz.utc), short_description=json_advisories[advisory].get('isummary', ''))
                db_advisory.save()
                for release, release_data in json_advisories[advisory]['releases'].items():
                    for package, package_data in release_data['sources'].items():
                        db_srcpackage = SourcePackage(advisory=db_advisory, package=package, release=release, safe_version=package_data['version'])
                        db_srcpackage.save()           
                    for package, package_data in release_data['binaries'].items():
                        db_binpackage = BinaryPackage(source_package=db_srcpackage, advisory=db_advisory, package=package, release=release, safe_version=package_data['version'])
                        db_binpackage.save()
            except:
                print "Error"
            else:
                print "OK"

class Command(BaseCommand):
    help = 'Update all sources of advisories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Updating DSAs..."))
        feed = DebianFeed()
        feed.update_local_database()

        print ""

        self.stdout.write(self.style.MIGRATE_HEADING("Updating USNs..."))
        feed = UbuntuFeed()
        feed.update_local_database()
