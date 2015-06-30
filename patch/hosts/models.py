from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Host(models.Model):
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer)
    hostinfo_fingerprint = models.CharField(max_length=200, unique=True)
    current_status = models.ForeignKey('HostStatus', related_name='+', null=True)

    def __unicode__(self):
        return self.name

    def active(self):
        return self.current_status.status == 'present'

class HostDiscoveryRun(models.Model):
    SOURCES = (
        ('hostinfo', 'hostinfo'),
    )

    source = models.CharField(choices=SOURCES, max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s run %s" % (self.source, self.created)

class HostStatus(models.Model):
    STATUSES = (
        ('present', 'present'),
        ('absent', 'absent'),
    )

    host = models.ForeignKey(Host)
    discovery_run = models.ForeignKey(HostDiscoveryRun)
    status = models.CharField(choices=STATUSES, max_length=32)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "host statuses"

    def __unicode__(self):
        return "%s was %s" % (self.host.name, self.status)
