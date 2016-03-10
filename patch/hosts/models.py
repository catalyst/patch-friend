from django.conf import settings
from django.db import models

# Customer models

class Customer(models.Model):
    """
    Represents one "customer organisation" with its own set of tags, policies, hosts and contacts.
    """

    name = models.CharField(max_length=200, help_text="Name of customer.")

    def __unicode__(self):
        return self.name

# Host models

class Host(models.Model):
    """
    One computer.
    """

    STATUSES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    name = models.CharField(max_length=200, help_text="A name to refer to the host, usually the hostname.")
    customer = models.ForeignKey(Customer)
    hostinfo_fingerprint = models.CharField(max_length=200, unique=True, null=True, help_text="This host's fingerprint in hostinfo, if this host was created from hostinfo data.")
    hostinfo_id = models.IntegerField(null=True, verbose_name="Hostinfo ID", help_text="This host's ID in hostinfo, if this host was created from hostinfo data.")
    tags = models.ManyToManyField('Tag', help_text="Tags associated with this host.")
    architecture = models.CharField(max_length=200, help_text="Machine architecture.")
    release = models.CharField(max_length=200, help_text="Operating system release.")
    status = models.CharField(choices=STATUSES, max_length=32, help_text="Whether the host exists or not.")
    updated = models.DateTimeField(auto_now_add=True, help_text="When this status was discovered.")

    def __unicode__(self):
        return self.name

class HostImportedAttribute(models.Model):
    """
    Stores arbitrary key/value information as collected from e.g. hostinfo or another external data source. Not currently used for much...
    """

    host = models.ForeignKey(Host)
    key = models.CharField(max_length=200, help_text="Attribute's key.")
    value = models.CharField(max_length=200, help_text="Attribute's value.")

    class Meta:
        unique_together = (("host", "key"),)

    def __unicode__(self):
        return self.key

# Package models

class Package(models.Model):
    """
    Operating system package.
    """

    STATUSES = (
        ('present', 'Installed'),
        ('absent', 'Removed'),
    )

    name = models.CharField(max_length=200, help_text="Name of package from the operating system's package manager.")
    host = models.ForeignKey(Host)
    status = models.CharField(choices=STATUSES, max_length=32, help_text="Whether the package is installed.")
    version = models.CharField(max_length=200, help_text="The package manager's version for this package.")
    architecture = models.CharField(max_length=200, help_text="Package architecture, which may differ from the host architecture.")

    class Meta:
        unique_together = (("name", "host"),)

    def __unicode__(self):
        return "%s" % self.name

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
