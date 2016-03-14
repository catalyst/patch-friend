from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import Count

from .models import *

# Host admin

class HostImportedAttributeInline(admin.TabularInline):
    model = HostImportedAttribute
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
            return queryset.filter(release__in=[rel for rel, name in settings.RELEASES])
        if self.value() == 'unsupported':
            return queryset.exclude(release__in=[rel for rel, name in settings.RELEASES])

class PackageInline(admin.StackedInline):
    model = Package
    extra = 0
    readonly_fields = ['status']
    fields = ['status']

class HostAdmin(admin.ModelAdmin):
    inlines = [HostImportedAttributeInline, PackageInline]
    search_fields = ['name']
    list_display = ['name', 'release', 'hostinfo_fingerprint', 'package_count']
    list_filter = ['status', 'release', 'architecture', HostSupportedListFilter]

    def get_queryset(self, request):
        return Host.objects.annotate(package_count=Count('package'))

    def package_count(self, instance):
        return instance.package_count

# Package admin

class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'status']
    search_fields = ['name']

# Tag admin

class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "customer"]

# Customer admin

class HostInline(admin.StackedInline):
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
admin.site.register(Package, PackageAdmin)
admin.site.register(Tag, TagAdmin)
