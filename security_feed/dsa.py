#!/usr/bin/env python

import re
import os

import pysvn

from base import SecurityFeed

class DebianFeed(SecurityFeed):

    def __init__(self, secure_testing_url=None, cache_location=None):
        self.client = pysvn.Client()
        self.secure_testing_url = secure_testing_url or 'svn://anonscm.debian.org/svn/secure-testing'
        self.cache_location = cache_location or '%s/.security-feed/dsa/cache' % os.environ['HOME']

    def _update_repository(self):
        return
        number = self.client.update(self.cache_location)[0].number

        if number == -1: # the repo doesn't exist yet in the cache
            self.client.checkout(self.secure_testing_url, self.cache_location)


    def get_advisories(self):
        self._update_repository()
        with open('%s/data/DSA/list' % self.cache_location) as dsa_list_file:
            dsa = ''
            packages = {}
            for line in dsa_list_file:
                if line.startswith('['): # start of the DSA
                    print dsa, packages
                    dsa = line.split('] ')[-1].split()[0]
                    description = line.split(' - ')[-1].strip() if ' - ' in line else ''
                    packages = {}
                elif line.startswith('\t[') and '<not-affected>' not in line: # source package name for a particular release
                    release = line.split()[0].strip("\t[] ")
                    version = line.split()[3]
                    source_package = line.split()[2]
                    if source_package not in packages:
                        packages[source_package] = {}
                    packages[source_package][release] = version



if __name__ == "__main__":
    feed = DebianFeed()
    print feed.get_advisories()
