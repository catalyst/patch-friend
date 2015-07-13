Overview
========

The objectives of Patch Friend are several. The order in which features are implemented will loosely follow these objectives.

Objectives
----------

Patch Friend will aggregate information from as many sources of "advisories" as is necessary to cover the hosts in its database. Currently this is Ubuntu USNs and Debian DSAs. This advisory information will be digested in to a common format.

Information about what packages are installed on all managed hosts will be collected and aggregated from the available sources. Currently this is just hostinfo, though it would be logical to produce a plugin using mcollective to collect this information more frequently, and eventually to provide a bare bones "native" plugin that can independently collect package data (for use mostly outside of Catalyst contexts).

Should be the authoritative source of data about:

- Which hosts belong to which customer
- Responsible people for that customer in an administrative and technical capacity
- Patching policies, both automated and manual, that apply to the machines belonging to that customer
- Groupings or 'tags' applied to hosts
- Packages installed on each host
- Other things?

Eventually Patch Friend should be a data source for puppet to permit the configuration of machineinfo files, patching policies and maybe even package upgrades from its central database.

Timeline
--------

Here's a rough outline:

#. Collect and parse advisory information in to database
     This is done for Debian and Ubuntu. The code is pretty tidy.
#. Collect information from hostinfo in to the database
     Works however it needs some work, see todo section.
#. Produce reports per-advisory per-customer grouped by patching policy showing affected machines (to replace existing reports)
#. Produce reports per-advisory showing number of hosts to which the advisory applies, and portion remediated
#. Produce reports per-customer grouped by patching policy showing hosts with outstanding advisories
#. Add a basic UI for sysadmins to rate the severity of an advisory? Idea needs development
#. Add data model for "remediation" for combination of host + advisory, customer + advisory, customer + tag + advisory. To allow sysadmins to mark a host as "patched" (or otherwise remediated) in the first instance, and as a way to bulk mark an advisory as being "compensated" for certain groups of hosts.
#. Add a basic UI for sysadmins to tick off hosts as "patched" as they go
#. Permit non-technical for a particular "customer" to log in and see view of hosts and their statuses
#. Add data model for "automated patching policy" for combinations of customer + tag. To permit the creation of custom "semi-automatic" policies (e.g. patching nightly / on specified day at specified time, reboot on certain day of week at certain time or nightly, as required) and apply these policies to certain combinations of customer + tag. This would allow Patch Friend to automatically mark these hosts as "compensated", saving manual intervention by the sysadmin
#. Export this data in to puppet to permit the automated configuration of these policies (a new puppet module is planned for this)
#. Convince all customers and PMs to make all dev and staging machines full automatic :)

Current problems
----------------

- Binary package information is not directly available for Debian packages. An assumption is made that binary packages in Debian share the version number of their source package. This may be intractable. For now, a manageable solution is to just have manual edits made as required.
- No support for squeeze LTS. Not sure how to solve this. Probably by upgrading the boxes affected to stable or oldstable...

Jobs to do
----------

- Fix the hostinfo discovery process so that new package statuses are only generated during a run if the status of the package has changed. Storage will be a problem otherwise, and this will address the current performance problems. Check for assumptions about the presence of a PackageStatus in a given PackageDiscoveryRun.
- Tidy and document the hostinfo code, it is crufty
- Tidy up the customer and tag data for imported hosts
- Add a "hostinfo_name" to Customer to permit matching of hostinfo CLIENT data to renamed Customers in our database
- Basic report output
- More documentation on workflows (Michael to provide)
