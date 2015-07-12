from django.conf import settings
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer)

    class Meta:
        unique_together = (("name", "customer"),)

    def __unicode__(self):
        return self.name

class Host(models.Model):
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer)
    hostinfo_fingerprint = models.CharField(max_length=200, unique=True, null=True)
    hostinfo_id = models.IntegerField(null=True, verbose_name="Hostinfo ID")
    current_status = models.ForeignKey('HostStatus', related_name='+', null=True)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name

    def active(self):
        return self.current_status.status == 'present'

class HostDiscoveryRun(models.Model):
    source = models.CharField(choices=settings.DATA_SOURCES, max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s host run %s" % (self.source, self.created)

class HostStatus(models.Model):
    STATUSES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    host = models.ForeignKey(Host)
    discovery_run = models.ForeignKey(HostDiscoveryRun)
    status = models.CharField(choices=STATUSES, max_length=32)
    release = models.CharField(choices=settings.RELEASES,max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("host", "discovery_run"),)

    class Meta:
        verbose_name_plural = "host statuses"

    def __unicode__(self):
        return self.status

class HostImportedAttribute(models.Model):
    host = models.ForeignKey(Host)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    class Meta:
        unique_together = (("host", "key"),)

    def __unicode__(self):
        return self.key

class Package(models.Model):
    name = models.CharField(max_length=200)
    host = models.ForeignKey(Host)
    current_status = models.ForeignKey('PackageStatus', related_name='+', null=True)

    class Meta:
        unique_together = (("name", "host"),)

    def __unicode__(self):
        return "%s" % self.name

class PackageDiscoveryRun(models.Model):
    host = models.ForeignKey(Host)
    source = models.CharField(choices=settings.DATA_SOURCES, max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s package run %s" % (self.host.name, self.source, self.created)

class PackageStatus(models.Model):
    STATUSES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )

    package = models.ForeignKey(Package)
    discovery_run = models.ForeignKey(PackageDiscoveryRun)
    status = models.CharField(choices=STATUSES, max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "package statuses"
        unique_together = (("package", "discovery_run"),)

    def __unicode__(self):
        if self.status == 'present':
            return self.version
        else:
            return "not installed" 
