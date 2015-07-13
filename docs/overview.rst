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

Current problems
----------------

- Binary package information is not directly available for Debian packages. An assumption is made that binary packages in Debian share the version number of their source package. This may be intractable. For now, a manageable solution is to just have manual edits made as required.
- No support for squeeze LTS. Not sure how to solve this. Probably by upgrading the boxes affected to stable or oldstable...
