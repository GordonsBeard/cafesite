from filebrowser.sites import site
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',                          'cafe.views.index'),
    url(r'^admin/',                     include(admin.site.urls)),
    url(r'^news/',                      include('news.urls')),
    url(r'^post/',                      include('news.urls')),
    url(r'^tag/(?P<tagname>[-\w]+)/$',  'news.views.tagged_items'),
    url(r'^newpost/',                   'cafe.views.index'),
    url(r'^admin/filebrowser/',         include(site.urls)),
    url(r'^user/',                      include('cafe.userurls')),
    url(r'^comments/$',                 'news.views.comment_listing'),
    url(r'^game/',                      include('news.caturls')),
    url(r'^openid/complete/$',          'cafe.views.login'),
    url(r'^openid/',                    include('django_openid_auth.urls')),
    url(r'^logout/$',                   'cafe.views.logout_view'),
    #url(r'^pysg/',                      include('pysg_django.urls')),
    url(r'comments/posted/$',           'news.views.comment_posted'),
    url(r'^comments/',                  include('django.contrib.comments.urls')),
    #url(r'^stats/',                     include('cafe.statsurls')),
    url(r'^grappelli/',                 include('grappelli.urls')),
    url(r'^ckeditor/',                  include('ckeditor.urls')),
    url(r'^server/',                    include('srcquery.urls')),
    url(r'^map/(?P<mapname>.+)/$',      'srcquery.views.map_detail'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
