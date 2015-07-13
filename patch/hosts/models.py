from django.conf import settings
from django.db import models

# Customer models

class Customer(models.Model):
    """
    Represents one "customer organisation" with its own set of tags, policies, hosts and contacts.
    """

    name = models.CharField(max_length=200, description="Name of customer")

    def __unicode__(self):
        return self.name

# Host models

class Host(models.Model):
    """
    One computer.
    """

    name = models.CharField(max_length=200, description="A name to refer to the host, usually the hostname")
    customer = models.ForeignKey(Customer)
    hostinfo_fingerprint = models.CharField(max_length=200, unique=True, null=True, description="This host's fingerprint in hostinfo, if this host was created from hostinfo data")
    hostinfo_id = models.IntegerField(null=True, verbose_name="Hostinfo ID", description="This host's ID in hostinfo, if this host was created from hostinfo data")
    current_status = models.ForeignKey('HostStatus', related_name='+', null=True, description="Direct reference to the newest status for this host")
    tags = models.ManyToManyField(Tag, description="Tags associated with this host")

    def __unicode__(self):
        return self.name

    def active(self):
        return self.current_status.status == 'present'

class HostDiscoveryRun(models.Model):
    """
    A collection of host statuses collected in one atomic operation from a particular data source (e.g. hostinfo). Used to see how the set of hosts in a particular source
    varies over time.
    """

    source = models.CharField(choices=settings.DATA_SOURCES, max_length=32, description="Data source from which this run was collected")
    created = models.DateTimeField(auto_now_add=True, description="Time at which the run started")

    def __unicode__(self):
        return "%s host run %s" % (self.source, self.created)

class HostImportedAttribute(models.Model):
    """
    Stores arbitrary key/value information as collected from e.g. hostinfo or another external data source. Not currently used for much...
    """

    host = models.ForeignKey(Host)
    key = models.CharField(max_length=200, description="Attribute's key")
    value = models.CharField(max_length=200, description="Attribute's value")

    class Meta:
        unique_together = (("host", "key"),)

    def __unicode__(self):
        return self.key

class HostStatus(models.Model):
    """
    The temporally-relevant information about a particular host, as collected during a host discovery run.
    """

    STATUSES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    host = models.ForeignKey(Host)
    discovery_run = models.ForeignKey(HostDiscoveryRun)
    status = models.CharField(choices=STATUSES, max_length=32, description="Set to the new status of the host if it has changed since the last run from this source")
    release = models.CharField(choices=settings.RELEASES,max_length=32, description="The operating system release of the host")
    created = models.DateTimeField(auto_now_add=True, description="When this status was discovered")

    class Meta:
        unique_together = (("host", "discovery_run"),)

    class Meta:
        verbose_name_plural = "host statuses"

    def __unicode__(self):
        return self.status

# Package models

class Package(models.Model):
    """
    Operating system package.
    """

    name = models.CharField(max_length=200, description="Name of package from the operating system's package manager")
    host = models.ForeignKey(Host)
    current_status = models.ForeignKey('PackageStatus', related_name='+', null=True, description="Direct reference to the newest status for this package")

    class Meta:
        unique_together = (("name", "host"),)

    def __unicode__(self):
        return "%s" % self.name

class PackageDiscoveryRun(models.Model):
    """
    A collection of package statuses collected in one atomic operation from a particular data source (e.g. hostinfo). Used to see how the set of packages in a particular source
    varies over time.
    """

    host = models.ForeignKey(Host)
    source = models.CharField(choices=settings.DATA_SOURCES, max_length=32, description="Data source from which this run was collected")
    created = models.DateTimeField(auto_now_add=True, description="When this status was discovered")

    def __unicode__(self):
        return "%s %s package run %s" % (self.host.name, self.source, self.created)

class PackageStatus(models.Model):
    """
    The temporally-relevant information about a particular package, as collected during a package discovery run.
    """

    STATUSES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    package = models.ForeignKey(Package)
    discovery_run = models.ForeignKey(PackageDiscoveryRun)
    status = models.CharField(choices=STATUSES, max_length=32, description="Set to the new status of the package if it has changed since the last run from this source")
    created = models.DateTimeField(auto_now_add=True, description="When this status was discovered")
    version = models.CharField(max_length=200, description="The package manager's version for this package")

    class Meta:
        verbose_name_plural = "package statuses"
        unique_together = (("package", "discovery_run"),)

    def __unicode__(self):
        if self.status == 'present':
            return self.version
        else:
            return "not installed" 

# Tag models

class Tag(models.Model):
    """
    An identifying tag that can be applied to hosts in a particular customer, and used to later specify which policies apply to those hosts.
    """
    
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer)

    class Meta:
        unique_together = (("name", "customer"),)

    def __unicode__(self):
        return self.name
