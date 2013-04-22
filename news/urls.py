from django.conf.urls import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('news.views',
    url(r'^$',                      'index'),
    url(r'^(?P<slug>[-\w]+)/$',     'detail'),
)
