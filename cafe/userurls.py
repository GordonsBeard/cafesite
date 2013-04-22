from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('cafe.views',
    url(r'^(?P<id>\d+)/$',                          'user_index'),
    url(r'^(?P<id>\d+)/posts/$',                    'user_posts'),
    url(r'^(?P<id>\d+)/posts/(?P<cat>.{5,}?)/$',      'user_posts'),
    url(r'^(?P<id>\d+)/comments/$',                 'user_comments'),
    url(r'^(?P<id>\d+)/comments/(?P<cat>.{5,}?)/$',   'user_comments'),
)
