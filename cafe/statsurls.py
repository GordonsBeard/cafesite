from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('cafe.views',
    url(r'^$',                          'stats_index'),
)
