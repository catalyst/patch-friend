from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Count

from .models import *
from admin_helpers import InlineEditLinkMixin

class HostSupportedListFilter(admin.SimpleListFilter):
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

class PackageInline(InlineEditLinkMixin, admin.StackedInline):
    model = Package
    extra = 0
    readonly_fields = ['current_status']
    fields = ['current_status']

class HostStatusInline(admin.StackedInline):
    model = HostStatus
    extra = 0

class TagInline(admin.StackedInline):
    model = Tag
    extra = 0

class HostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['current_status'].queryset = HostStatus.objects.filter(host=self.instance)
        try:
            self.fields['tags'].queryset = Tag.objects.filter(customer=self.instance.customer)
        except:
            pass

class HostInline(admin.StackedInline):
    form = HostForm
    model = Host
    extra = 0

class HostImportedAttributeInline(admin.TabularInline):
    model = HostImportedAttribute
    extra = 0



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

class HostDiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ["source", "created"]

class PackageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PackageForm, self).__init__(*args, **kwargs)
        self.fields['current_status'].queryset = PackageStatus.objects.filter(package=self.instance)

class PackageStatusForm(forms.ModelForm):
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

class PackageDiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ["host", "source", "created"]

class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "customer"]

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name']   
    inlines = [TagInline, HostInline]
    search_fields = ['name']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(HostDiscoveryRun, HostDiscoveryRunAdmin)
admin.site.register(PackageDiscoveryRun, PackageDiscoveryRunAdmin)

admin.site.register(Package, PackageAdmin)
admin.site.register(PackageStatus)

admin.site.register(Tag, TagAdmin)
