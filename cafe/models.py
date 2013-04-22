from django.db import models
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from news.models import NewsPost

class UserProfile(models.Model):
    LEVEL_NAMES = (
        (u'0',  u'Staff'),
        (u'1',  u'Cool Kid'),
        (u'2',  u'Regular'),
        (u'3',  u'Patron'),
    )

    user = models.OneToOneField(User)

    # This will update their steam information every time they log in or something I guess yeah that sounds good.
    handle = models.CharField(max_length=50, blank=True)
    steamid = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=255, blank=True)
    avatar = models.CharField(max_length=255, blank=True)
    avatarM = models.CharField(max_length=255, blank=True)
    avatarL = models.CharField(max_length=255, blank=True)
    primarygroup = models.CharField(max_length=50, blank=True)
    realname = models.CharField(max_length=50, blank=True)

    # This is the cafe stuff
    level = models.CharField(max_length=2, choices=LEVEL_NAMES, blank=True)

    def get_postcount(self):
        return NewsPost.objects.filter(author=self.user).count()

    def get_commentcount(self):
        return Comment.objects.filter(user=self.user).count()

    def __unicode__(self):
        return self.handle

def create_user_profile(sender, instance, created, **kw):
    if created:
        UserProfile.objects.create(user=instance)


