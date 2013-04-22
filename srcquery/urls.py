from django.conf.urls import patterns, url

urlpatterns = patterns('srcquery.views',
    url(r'^$',              'server_listing'),
    url(r'^(?P<slug>.+)/maps/$', 'server_maps'),
    url(r'^(?P<slug>.+)/$', 'server_detail'),
)
