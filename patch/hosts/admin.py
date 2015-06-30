from django.contrib import admin

from .models import *

class HostActivityListFilter(admin.SimpleListFilter):
    title = 'activity'
    parameter_name = 'activity'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(current_status__status='present')
        if self.value() == 'inactive':
            return queryset.filter(current_status__status='absent')

class HostStatusInline(admin.StackedInline):
    model = HostStatus
    extra = 0

class HostAdmin(admin.ModelAdmin):
    inlines = [HostStatusInline]
    search_fields = ['name']
    list_display = ['name', 'hostinfo_fingerprint']
    list_filter = [HostActivityListFilter]

class HostDiscoveryRunAdmin(admin.ModelAdmin):
    list_display = ["source", "created"]

admin.site.register(Customer)
admin.site.register(Host, HostAdmin)
admin.site.register(HostDiscoveryRun, HostDiscoveryRunAdmin)
