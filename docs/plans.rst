Plans and designs
=================

Some random notes on design things.

Version comparisons
-------------------

For Debian-like packages I suggest we use http://pgxn.org/dist/debversion/ to create a custom model field type, permitting accurate comparisons of package versions.

Other OSes will need further investigation in to suitable methods.

Host - advisory relationship
----------------------------

The relationship between a particular host and advisory should be in one of these states. The names of these states are not set in stone but should be decided soon...

- Not applicable (e.g. the host is not running an affected release or does not have the package installed)
- Fixed (e.g. the host is "applicable" but the running version is newer than or equal to the safe version)
- Vulnerable (e.g. the host is "applicable" but the running version is older than the safe version)
- Compensated (e.g. either a sysadmin has indicated that they have patched the vulnerability or resolved it in some other way OR the local evaluation of the patching policy suggests it will be automatically resolved)

It may be worth having a more fine grained set of states for "Compensated", e.g. "awaiting automatic resolution" for automated policies vs "has been patched already".

It is expected that packages will fall from Compensated in to Fixed over time as "marked as fixed" is upgraded to "definitely fixed" on receipt of more up to date package data.

Places in which overrides may be added
--------------------------------------

It should be possible eventually to override the status of a particular advisory at these levels:

- Per host
- Per tag
- Per customer
- Globally

E.g. to mark an adivsory as "compensated" for a whole tag group, without needing to specifically mark it on each host.
