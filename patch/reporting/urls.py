from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.OverviewView.as_view(), name='overview'),
    url(r'^hosts/$', views.HostIndexView.as_view(), name='host_list'),
    url(r'^hosts/(?P<slug>[^/]+)/$', views.HostDetailView.as_view(), name='host_detail'),
    url(r'^advisories/$', views.AdvisoryIndexView.as_view(), name='advisory_list'),
    url(r'^advisories/(?P<slug>[-\w]+)/$', views.AdvisoryDetailView.as_view(), name='advisory_detail'),
    url(r'^advisories/(?P<advisory>[-\w]+)/remaining_hosts.csv$', views.AdvisoryHostListView.as_view(), name='advisory_hostlist'),
]
