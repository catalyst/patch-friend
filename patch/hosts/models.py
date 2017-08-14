from django.conf import settings
from django.db import models

# Customer models

class Customer(models.Model):
    """
    Represents one "customer organisation" with its own set of tags, policies, hosts and contacts.
    """

    name = models.CharField(max_length=200, help_text="Name of customer.")

    def __str__(self):
        return self.name

# Host models

class Host(models.Model):
    """
    One computer.
    """

    SOURCES = (
        ('hostinfo', 'hostinfo'),
    )

    name = models.CharField(max_length=200, help_text="A name to refer to the host, usually the hostname.")
    customer = models.ForeignKey(Customer)
    hostinfo_fingerprint = models.CharField(max_length=200, unique=True, null=True, help_text="This host's fingerprint in hostinfo, if this host was created from hostinfo data.")
    hostinfo_id = models.IntegerField(null=True, verbose_name="Hostinfo ID", help_text="This host's ID in hostinfo, if this host was created from hostinfo data.")
    tags = models.ManyToManyField('Tag', help_text="Tags associated with this host.")
    architecture = models.CharField(max_length=200, help_text="Machine architecture.")
    release = models.CharField(max_length=200, help_text="Operating system release.")
    updated = models.DateTimeField(auto_now_add=True, help_text="When this status was discovered.")
    source = models.CharField(choices=SOURCES, max_length=32, help_text="Source of this host's data.")
    host_hash = models.CharField(max_length=64, null=True, help_text="The hash of all the fields of the object, used for detecting changes.")

    def __str__(self):
        return self.name

    def tag_group(self, separator=", "):
        """
        A string that can be used to group this host with others having the same tag set.
        """

        return separator.join(sorted(list([tag.name.strip().lower() for tag in self.tags.all()]))).strip()

    def packages_affected_by_advisory(self, advisory):
        return self.package_set.filter(advisory._affected_packages_query(self.release))

class HostImportedAttribute(models.Model):
    """
    Stores arbitrary key/value information as collected from e.g. hostinfo or another external data source. Not currently used for much...
    """

    host = models.ForeignKey(Host)
    key = models.CharField(max_length=200, help_text="Attribute's key.")
    value = models.CharField(max_length=200, help_text="Attribute's value.")

    class Meta:
        unique_together = (("host", "key"),)

    def __str__(self):
        return self.key

# Package models

# class DebversionField(models.Field):
#     """
#     Field type from `postgresql-9.4-debversion' package in Debian.
#     """
#
#     def db_type(self, connection):
#         return 'debversion'

class Package(models.Model):
    """
    Operating system package.
    """

    name = models.CharField(max_length=200, help_text="Name of package from the operating system's package manager.")
    host = models.ForeignKey(Host)
    version = models.CharField(max_length=200, help_text="The package manager's version for this package.")
    architecture = models.CharField(max_length=200, help_text="Package architecture, which may differ from the host architecture.")

    class Meta:
        unique_together = (("name", "host", "architecture"),)

    def __str__(self):
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

    def __str__(self):
        return self.name
