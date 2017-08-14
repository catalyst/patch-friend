import apt_pkg
apt_pkg.init_system()

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from hosts.models import Host, Package

class Advisory(models.Model):
    """
    "Lowest common denominator" across all vendor advisories.
    """

    upstream_id = models.CharField(max_length=200, verbose_name="Upstream ID", help_text="The ID used by the vendor to refer to this advisory")
    short_description = models.CharField(max_length=200, null=True, help_text="One-line description of the advisory")
    description = models.TextField(null=True, help_text="Longer description of the advisory")
    action = models.TextField(null=True, help_text="What, if any, actions need to be taken to address the advisory")
    issued = models.DateTimeField(default=timezone.now, help_text="Date and time at which the advisory was issued")
    source = models.CharField(choices=settings.ADVISORY_SOURCES, max_length=32, help_text="Vendor source of the advisory")
    severity = models.IntegerField(blank=True, choices=settings.ADVISORY_SEVERITIES, default=0, help_text="Local severity of the advisory, once it has been reviewed")
    reviewed_by = models.ForeignKey(User, blank=True, null=True, help_text="Person who locally reviewed the advisory for its overall severity (or None if the severity was determined automatically)")
    search_keywords = models.TextField(blank=True, null=True, help_text="Space separated list of keywords used to speed up search")
    affected_hosts = models.ManyToManyField(Host, through='Problem', help_text="All hosts that have a problem with this advisory")

    class Meta:
        verbose_name_plural = "advisories"
        ordering = ["-issued"]

    def __str__(self):
        return self.upstream_id


    # This is a function while affected hosts is a variable... TODO: decide what to do
    def unresolved_hosts(self):
        # print("unresolved:", Host.objects.filter(problem__fixed__isnull=True, problem__advisory=self))
        return Host.objects.filter(problem__fixed__isnull=True, problem__advisory=self)

    # Returns a set currently. TODO: do this properly
    def resolved_hosts(self):
        # print("\n1")
        # print(set(self.affected_hosts.distinct().all()))
        # print("\n\n2")
        # print(set(self.unresolved_hosts().distinct().all()))
        # for prob in Problem.objects.filter(advisory=self) :
        #     print(prob)
        # print("\n\n3")
        # print(set(self.affected_hosts.distinct().all()) - set(self.unresolved_hosts().distinct().all()))
        # print("end\n")
        return set(self.affected_hosts.distinct().all()) - set(self.unresolved_hosts().distinct().all())

    # These can be done much better. TODO: redo these
    def resolved_hosts_percentage(self):
        return (float(len(self.resolved_hosts()))/float(self.affected_hosts.distinct().count()))*100

    def unresolved_hosts_percentage(self):
        return ((float(self.unresolved_hosts().distinct().count()))/float(self.affected_hosts.distinct().count()))*100



    def _affected_packages_query(self, release):
        queries = None

        for package in self.binarypackage_set.filter(release=release):
            query = Q(name=package.package, version__lt=package.safe_version)

            if queries is None:
                queries = query
            else:
                queries = queries | query

        return queries

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('advisory_detail', args=(self.upstream_id, ))

    def source_package_names(self):
        return ", ".join([package.__str__() for package in self.sourcepackage_set.all()])

    def source_url(self):
        return dict(settings.SOURCE_ADVISORY_DETAIL_URLS)[self.source] % self.upstream_id


class SourcePackage(models.Model):
    """
    Source package to which an advisory refers. These are not of a direct concern to hosts, as source packages are not actually "installed".

    For Debian advisories, the source package is used to determine what binary packages (and their versions) are considered safe.
    """

    advisory = models.ForeignKey(Advisory, help_text="Advisory to which this package belongs")
    package = models.CharField(max_length=200, help_text="Name of source package")
    release = models.CharField(choices=settings.RELEASES,max_length=32, help_text="Specific release to which this package belongs")
    safe_version = models.CharField(max_length=200, help_text="Package version that is to be considered 'safe' at the issue of this advisory")

    class Meta:
        verbose_name_plural = "source packages"
        ordering = ["-package"]

    def __str__(self):
        safe_version = self.safe_version

        if self.safe_version == '0':
            safe_version = ''

        return "%s %s (%s)" % (self.package, safe_version, self.release)

    def source_url(self):
        return dict(settings.SOURCE_PACKAGE_DETAIL_URLS)[self.advisory.source] % (self.release, self.package)

class BinaryPackage(models.Model):
    """
    Binary package to which an advisory refers.

    In the case of Ubuntu, these are resolved directly from the supplied JSON data. For Debian these will be generated based on the source packages
    associated with this advisory.

    If source_package is null it is because this binary package was created directly from external data, rather than being generated locally.
    """

    advisory = models.ForeignKey(Advisory, help_text="Advisory to which this package belongs")
    source_package = models.ForeignKey(SourcePackage, blank=True, null=True, help_text="If set, the source package from which this binary package was generated")
    package = models.CharField(max_length=200, help_text="Name of binary package")
    release = models.CharField(choices=settings.RELEASES,max_length=32, help_text="Specific release to which this package belongs")
    safe_version = models.CharField(max_length=200, null=True, help_text="Package version that is to be considered 'safe' at the issue of this advisory")
    architecture = models.CharField(max_length=200, null=True, help_text="Machine architecture")

    class Meta:
        verbose_name_plural = "binary packages"
        ordering = ["-package"]

    def __str__(self):
        if self.safe_version:
            return "%s %s (%s, %s)" % (self.package, self.safe_version, self.release, self.architecture)
        else:
            return "%s (%s, %s)" % (self.package, self.release, self.architecture)

    def source_url(self):
        return dict(settings.SOURCE_PACKAGE_DETAIL_URLS)[self.advisory.source] % (self.release, self.package)

class Problem(models.Model):
    """
    Records the details around why a host is affected by an advisory.
    """

    advisory = models.ForeignKey(Advisory, help_text="Advisory that has caused this problem")
    host = models.ForeignKey(Host, help_text="Host which has the problem")

    installed_package_name = models.CharField(max_length=200, help_text="Name of binary package causing the problem", verbose_name='Package name')
    installed_package_version = models.CharField(max_length=200, help_text="Version of binary package causing the problem", verbose_name='Version')
    installed_package_architecture = models.CharField(max_length=200, help_text="Architecture of binary package causing the problem", verbose_name='Architecture')
    safe_package = models.ForeignKey(BinaryPackage, help_text="The safe package version provided by the advisory")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Discovered")
    fixed = models.DateTimeField(null=True)
    fixed_by = models.CharField(null=True, choices=settings.FIX_REASONS, max_length=200, help_text="Way in which the problem was resolved")

    class Meta:
        verbose_name_plural = "problems"

    def __str__(self):
        return "%s: %s %s on %s" % (self.advisory, self.installed_package_name, self.installed_package_version, self.host)

    def is_fixed(self):
        return self.fixed is not None and timezone.now() >= self.fixed
    is_fixed.boolean = True


@receiver(post_save, sender=BinaryPackage)
def cache_applicable_hosts_for_advisory_package(sender, **kwargs):
    """
    When a new package is added to an advisory work out what hosts it applies to.
    """

    advisory_package = kwargs.get('instance')
    advisory = advisory_package.advisory
    print("Considering advisory package %s (%s)" % (advisory_package.package, advisory_package.architecture))
    affected_packages = Package.objects.filter(name=advisory_package.package, architecture=advisory_package.architecture, host__release=advisory_package.release)

    for package in affected_packages:
        unsafe = apt_pkg.version_compare(str(package.version), str(advisory_package.safe_version)) < 0
        print("%s installed on %s is unsafe=%r due to installed version %s being <= %s" %(package.name, package.host, unsafe, package.version, advisory_package.safe_version))
        if unsafe:
            Problem.objects.get_or_create(advisory=advisory, host=package.host, installed_package_name=package.name, installed_package_version=package.version, installed_package_architecture=package.architecture, safe_package=advisory_package, fixed__isnull=True)
        else: # remove any problems that might have existed due to older incarnations of this advisory
            Problem.objects.filter(advisory=advisory, host=package.host, installed_package_name=package.name, installed_package_version=package.version, installed_package_architecture=package.architecture, safe_package=advisory_package).delete()


@receiver(post_save, sender=Package)
def add_package_to_host(sender, **kwargs):
    """
    When a package is added to a host find any advisories that apply to it and create problems.
    """

    package = kwargs.get('instance')
    print("installed %s on %s" % (package, package.host))
    advisory_packages = BinaryPackage.objects.filter(package=package.name, architecture=package.architecture, release=package.host.release)

    for advisory_package in advisory_packages:
        advisory = advisory_package.advisory
        unsafe = apt_pkg.version_compare(str(package.version), str(advisory_package.safe_version)) < 0
        print("%s installed on %s is unsafe=%r due to installed version %s being <= %s" %(package.name, package.host, unsafe, package.version, advisory_package.safe_version))
        if unsafe:
            Problem.objects.get_or_create(advisory=advisory, host=package.host, installed_package_name=package.name, installed_package_version=package.version, installed_package_architecture=package.architecture, safe_package=advisory_package, fixed__isnull=True)


@receiver(pre_delete, sender=Package)
def remove_package_from_host(sender, **kwargs):
    """
    When a package is removed from a host find any problems removing it might solve.
    """

    #TODO: Check if removing package resolves any affected hosts

    package = kwargs.get('instance')
    print("removed %s from %s" % (package, package.host))
    Problem.objects.filter(host=package.host, installed_package_name=package.name, installed_package_version=package.version, installed_package_architecture=package.architecture).update(fixed=timezone.now(), fixed_by='removed')
