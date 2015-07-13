from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Count

from .models import *

# Host admin

class HostForm(forms.ModelForm):
    """
    Override the standard host form to ensure that the host's current status can only be selected from the host's statuses and that 
    the tags can only be selected from the tags available in the Customer (if any).
    """

    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['current_status'].queryset = HostStatus.objects.filter(host=self.instance)
        try:
            self.fields['tags'].queryset = Tag.objects.filter(customer=self.instance.customer)
        except:
            pass

class HostImportedAttributeInline(admin.TabularInline):
    model = HostImportedAttribute
    extra = 0

class HostStatusInline(admin.StackedInline):
    model = HostStatus
    extra = 0

class HostSupportedListFilter(admin.SimpleListFilter):
    """
    Filter for whether or not a host's release in its latest status is in the list of supported releases or not.
    """

    title = 'support'
    parameter_name = 'support'

    def lookups(self, request, model_admin):
        return (
            ('supported', 'Supported'),
            ('unsupported', 'Out of support'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'supported':
            return queryset.filter(current_status__release__in=[rel for rel, name in settings.RELEASES])
        if self.value() == 'unsupported':
            return queryset.exclude(current_status__release__in=[rel for rel, name in settings.RELEASES])

class PackageInline(admin.StackedInline):
    model = Package
    extra = 0
    readonly_fields = ['current_status']
    fields = ['current_status']

class HostAdmin(admin.ModelAdmin):
    form = HostForm
    inlines = [HostImportedAttributeInline, PackageInline, HostStatusInline]
    search_fields = ['name']
    list_display = ['name', 'customer', 'release', 'hostinfo_fingerprint', 'package_count']
    list_filter = ['current_status__status', 'current_status__release', HostSupportedListFilter]

    def get_queryset(self, request):
        return Host.objects.annotate(package_count=Count('package'))

    def package_count(self, instance):
        return instance.package_count

    def release(self, instance):
        return instance.current_status.release

# Host discovery run admin

class HostDiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ["source", "created"]

# Package admin

class PackageForm(forms.ModelForm):
    """
    Override the standard package form to ensure that the package's current status can only be selected from the packages's statuses
    """

    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        self.fields['current_status'].queryset = PackageStatus.objects.filter(package=self.instance)

class PackageStatusForm(forms.ModelForm):
    """
    Override the standard package status form to ensure that the discovery run can only be selected from the packages's discovery runs
    """    

    def __init__(self, *args, **kwargs):
        super(PackageStatusForm, self).__init__(*args, **kwargs)
        try:      
            self.fields['discovery_run'].queryset = PackageDiscoveryRun.objects.filter(host=self.instance.package.host)
        except:
            pass

class PackageStatusInline(admin.StackedInline):
    form = PackageStatusForm
    model = PackageStatus
    extra = 0

class PackageAdmin(admin.ModelAdmin):
    form = PackageForm
    list_display = ['name', 'host', 'current_status']   
    inlines = [PackageStatusInline]
    search_fields = ['name']

# Package discovery run admin

class PackageDiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ["host", "source", "created"]

# Tag admin

class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "customer"]

# Customer admin

class HostInline(admin.StackedInline):
    form = HostForm
    model = Host
    extra = 0

class TagInline(admin.StackedInline):
    model = Tag
    extra = 0

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name']   
    inlines = [TagInline, HostInline]
    search_fields = ['name']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(HostDiscoveryRun, HostDiscoveryRunAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(PackageDiscoveryRun, PackageDiscoveryRunAdmin)
admin.site.register(PackageStatus)
admin.site.register(Tag, TagAdmin)
