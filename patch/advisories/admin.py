from django.contrib import admin

from .models import *

class BinaryPackageInline(admin.TabularInline):
    model = BinaryPackage
    extra = 0
    readonly_fields=('source_package',)
    fields = ('package', 'safe_version', 'architecture')

class SourcePackageInline(admin.TabularInline):
    model = SourcePackage
    extra = 0
    fields = ('package', 'release', 'safe_version')

class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 0
    readonly_fields = ('safe_package',)
    fields = ('host', 'installed_package_name', 'fixed', 'fixed_by')


class AdvisoryAdmin(admin.ModelAdmin):
    inlines = [ProblemInline, SourcePackageInline, BinaryPackageInline]
    list_filter = ['issued', 'source']
    search_fields = ['upstream_id']
    list_display = ['upstream_id', 'short_description', 'source_package_names', 'source', 'issued']
    ordering = ['-issued']

class ProblemFixedFilter(admin.SimpleListFilter):
    title = 'fix state'
    parameter_name = 'fixed'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Fixed'),
            ('false', 'Not fixed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(fixed__lte=timezone.now())
        if self.value() == 'false':
            return queryset.filter(fixed__isnull=True)

class ProblemAdmin(admin.ModelAdmin):
    list_display = ['host', 'advisory', 'installed_package_name', 'installed_package_version', 'installed_package_architecture', 'created', 'is_fixed']
    list_filter = [ProblemFixedFilter]
    readonly_fields = ('safe_package',)

admin.site.register(Advisory, AdvisoryAdmin)
admin.site.register(Problem, ProblemAdmin)
