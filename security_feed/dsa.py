#!/usr/bin/env python

import re
import os
import sqlite3

import deb822
import pysvn
import requests

from base import SecurityFeed

class DebianFeed(SecurityFeed):

    def __init__(self, secure_testing_url=None, cache_location=None, releases=None):
        self.client = pysvn.Client()
        self.secure_testing_url = secure_testing_url or 'svn://anonscm.debian.org/svn/secure-testing'
        self.cache_location = cache_location or '%s/.security-feed/dsa/cache' % os.environ['HOME']
        self.releases = releases or (
            'squeeze',
            'wheezy',
            'jessie',
        )
        self.db = sqlite3.connect('%s/db.sqlite3' % self.cache_location)
        self.cur = self.db.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS `advisories` (
                `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `debian_id` TEXT,
                `description`   TEXT
            );
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS `binary_packages` (
                `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `advisory_id`   INTEGER NOT NULL,
                `package`   TEXT NOT NULL,
                `release`   TEXT NOT NULL
            );
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS `source_packages` (
                `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                `advisory_id`   INTEGER NOT NULL,
                `package`   TEXT NOT NULL,
                `release`   TEXT NOT NULL,
                `safe_version`  TEXT NOT NULL
            );
        """)
        self.db.commit()

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
                            'description': description
                        }
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

    def _load_cached_advisories(self):
        return self.cur.execute('SELECT * from advisories;').fetchall()

    def _update_local_database(self):
        svn_advisories = self._parse_svn_advisories()
        new_advisories = set(svn_advisories) - set([row[1] for row in  self._load_cached_advisories()])

        print "%i new advisories to download" % len(new_advisories)

        for advisory in new_advisories:
            self.cur.execute('INSERT INTO advisories VALUES(NULL, ?, ?);', (advisory, svn_advisories[advisory]['description']))
            advisory_id = self.cur.lastrowid
            for package, versions in svn_advisories[advisory]['packages'].iteritems():
                for release, version in versions.iteritems():
                    try:
                        binary_packages = self._source_package_to_binary_packages(package, release)
                        for binary_package in binary_packages:
                            self.cur.execute('INSERT INTO binary_packages VALUES(NULL, ?, ?, ?);', (advisory_id, binary_package, release))
                    except:
                        print "could not get binary packages for %s/%s" % (release, package)
                    self.cur.execute('INSERT INTO source_packages VALUES(NULL, ?, ?, ?, ?);', (advisory_id, package, release, version))
                    self.db.commit()
                    print "retrieved binary packages for %s" % advisory

if __name__ == "__main__":
    feed = DebianFeed()
    import pprint; pprint.pprint(feed._update_local_database())
