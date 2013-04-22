from django import template
register = template.Library()
from django.conf import settings
from django.utils.safestring import mark_safe

@register.filter('read_more')
def read_more(body, absolute_url):
    if '<!--more-->' in body:
        return mark_safe(body[:body.find('<!--more-->')]+'<a href="'+str(absolute_url)+'">'+str(settings.READ_MORE_TEXT)+'</a>')
    else:
        return body
