import os
import re

import deb822
import pysvn
import pytz
import requests

from dateutil.parser import parse as dateutil_parse

from django.core.management.base import BaseCommand, CommandError
from advisories.models import *
from django.conf import settings

class SecurityFeed(object):
    pass

class DebianFeed(SecurityFeed):

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

    def _update_local_database(self):
        svn_advisories = self._parse_svn_advisories()
        new_advisories = set(svn_advisories) - set([advisory.upstream_id for advisory in Advisory.objects.all()])

        print "%i new advisories to download" % len(new_advisories)

        for advisory in new_advisories:
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
                        print "could not get binary packages for %s/%s" % (release, package)
                    print "retrieved binary packages for %s" % advisory

    def _parse_svn_advisories(self):
        self._update_repository()
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

class Command(BaseCommand):
    help = 'Update all sources of advisories'

    def handle(self, *args, **options):
        feed = DebianFeed()
        feed._update_local_database()

        self.stdout.write('Done')
