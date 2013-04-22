from datetime import timedelta
from django.db import models
from django.contrib.comments.models import Comment
from django.utils import timezone
from django.template.defaultfilters import slugify
from tagging.fields import TagField
import re

def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='img/icon')
    abv = models.CharField(max_length=5)
    tags = TagField()

    def get_absolute_url(self):
        return "/game/{0}".format(self.abv)

    class Meta:
        verbose_name_plural = "games"
        verbose_name = "game"

    def __unicode__(self):
        return self.name


class Blurb(models.Model):
    who = models.CharField(max_length=128)
    user = models.ForeignKey('auth.User', blank=True, null=True)
    said = models.CharField(max_length=435)
    pub_date = models.DateTimeField('when', blank=True, auto_now_add=True)


    def get_absolute_url(self):
        return "/blurb/{0}".format(self.id)

    def __unicode__(self):
        return "{0}: {1}".format(self.who, self.said[:140])

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    tags = TagField()
    category = models.ForeignKey('Category', blank=True, null=True)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey('auth.User')
    bulletin = models.BooleanField(blank=False, default=False)
    secret = models.CharField(max_length=32, blank=True)

    def save(self):
        if not self.id:
            unique_slugify(self, self.title)

        super(NewsPost, self).save()

    def get_absolute_url(self):
        return "/post/{0}".format(self.slug)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - timedelta(hours=1)

    def get_latest_comment(self):
        try:
            comment = Comment.objects.filter(object_pk=self.id).exclude(is_removed=True).order_by('-id')[0]
        except IndexError:
            comment = None
        return comment

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def __unicode__(self):
        return self.title
