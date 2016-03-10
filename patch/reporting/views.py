import collections

from django.conf import settings
from django.shortcuts import render
from django.views import generic

from extra_views import SearchableListMixin

from advisories.models import *

class AdvisoryIndexView(SearchableListMixin, generic.ListView):
    model = Advisory
    template_name = "reporting/advisory_list.html"
    paginate_by = 20
    search_fields = ['upstream_id']

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

        # have to convert back to dict to make the template work
        context['binary_packages'] = dict(binary_packages)

        return context
