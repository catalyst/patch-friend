import collections, csv
from urllib import urlencode

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from django.forms import model_to_dict
from extra_views import SearchableListMixin

from advisories.models import *

class AdvisoryIndexView(SearchableListMixin, generic.ListView):
    model = Advisory
    template_name = "reporting/advisory_list.html"
    paginate_by = 25
    search_fields = ['upstream_id', 'short_description', 'description', 'search_keywords', 'source']

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super(AdvisoryIndexView, self).get_context_data(**kwargs)
        context['paginate_by'] = self.request.GET.get('paginate_by', self.paginate_by)
        context['q'] = self.request.GET.get('q', '')
        context['pagination_extra'] = urlencode({'q': context['q'], 'paginate_by': context['paginate_by']})
        return context

class AdvisoryDetailView(generic.DetailView):
    model = Advisory
    slug_field = "upstream_id"
    template_name = "reporting/advisory_detail.html"

    def get_context_data(self, **kwargs):
        context = super(AdvisoryDetailView, self).get_context_data(**kwargs)

        # XXX this seems like a horrible way to do this but the tripled nested regroup in the template didn't work

        binary_packages = collections.defaultdict(dict)

        for package in context['object'].binarypackage_set.all():
            package_key = "%s %s" % (package.package, package.safe_version)

            if package_key not in binary_packages[package.release]:
                binary_packages[package.release][package_key] = {'package': package, 'architectures': []}

            binary_packages[package.release][package_key]['architectures'].append(package.architecture)

        unresolved_hosts = []
        for host in context['object'].unresolved_hosts():
            host_dict = {}
            host_dict['tag_group'] = host.tag_group()
            host_dict.update(model_to_dict(host))
            unresolved_hosts.append(host_dict)

        # have to convert back to dict to make the template work
        context['binary_packages'] = dict(binary_packages)
        context['aptget_command'] = settings.APTGET_COMMAND_STUB
        context['unresolved_hosts'] = unresolved_hosts

        return context

class AdvisoryHostListView(generic.View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % kwargs['advisory'].lower()
        advisory = get_object_or_404(Advisory, upstream_id=kwargs['advisory'])
        writer = csv.writer(response, quoting=csv.QUOTE_MINIMAL)

        for host in advisory.unresolved_hosts():
            writer.writerow([host.name, host.release])

        return response
