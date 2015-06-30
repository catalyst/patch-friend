from django.db import models
from django.utils import timezone

class Advisory(models.Model):
    SOURCES = (
        ('ubuntu', 'Ubuntu'),
        ('debian', 'Debian'),
    )

    upstream_id = models.CharField(max_length=200, verbose_name="Upstream ID")
    short_description = models.CharField(max_length=200)
    issued = models.DateTimeField(default=timezone.now)
    source = models.CharField(choices=SOURCES, max_length=32)    

    class Meta:
        verbose_name_plural = "advisories"

    def __unicode__(self):
        return self.upstream_id

    def source_package_names(self):
        return ", ".join([package.__unicode__() for package in self.sourcepackage_set.all()])

class SourcePackage(models.Model):
    RELEASES = (
        ('squeeze', 'squeeze'),
        ('wheezy', 'wheezy'),
        ('jessie', 'jessie'),
        ('precise', 'precise'),        
        ('trusty', 'trusty',)
    )

    advisory = models.ForeignKey(Advisory)
    package = models.CharField(max_length=200)
    release = models.CharField(choices=RELEASES,max_length=32)
    safe_version = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s < %s (%s)" % (self.package, self.safe_version, self.release)

class BinaryPackage(models.Model):
    RELEASES = (
        ('squeeze', 'squeeze'),
        ('wheezy', 'wheezy'),
        ('jessie', 'jessie'),
        ('precise', 'precise'),        
        ('trusty', 'trusty',)
    )

    advisory = models.ForeignKey(Advisory)
    source_package = models.ForeignKey(SourcePackage, null=True)
    package = models.CharField(max_length=200)
    release = models.CharField(choices=RELEASES,max_length=32)
    safe_version = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        if self.safe_version:
            return "%s < %s (%s)" % (self.package, self.safe_version, self.release)
        else:
            return "%s (%s)" % (self.package, self.release)

