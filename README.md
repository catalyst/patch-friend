# Patch friend

This application consumes the machine readable feeds of security advisories from the [Debian](https://debian.org/) and [Ubuntu](https://ubuntu.com) projects, and stores them in a database.

It can also receive a feed of hosts and their installed packages from either a [Hostinfo](http://git.catalyst.net.nz/gw?p=hostinfo.git;a=summary) installation, or directly from [osquery](https://osquery.io/) on the hosts themselves.

These two sources of information are used to produce reports about which hosts are impacted by which security vulnerabilities.

This application is a work in progress :)

## Bugs

python-apt isn't installable from pip (it has silent deps on things which are not in PyPi), so you may need to:

ln -s /usr/lib/python3/dist-packages/apt* $VIRTUAL_ENV/lib/python*/site-packages
And install python-apt in the host OS.
