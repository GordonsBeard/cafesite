from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.comments import Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django_openid_auth.models import UserOpenID
from django_openid_auth.views import parse_openid_response
from news.models import NewsPost, Category, Blurb
from news.forms import NewPostForm
from cafe.models import UserProfile
from tagging.models import Tag
import json
import urllib
import datetime
from itertools import chain

def index(request):
    try:
        post_list = NewsPost.objects.all()
    except IndexError:
        post_list = None

    try:
        blurb_list = Blurb.objects.all()
    except IndexError:
        blurb_list = None

    result_list = sorted(
        chain(post_list, blurb_list),
        key = lambda instance: instance.pub_date, reverse=True)

    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=2)

    if request.method == 'POST':
        f = NewPostForm(request.POST)
        if f.is_valid():
            newpost = f.save(commit=False)
            newpost.author = request.user
            newpost.pub_date = datetime.datetime.now()
            newpost.save()
            return HttpResponseRedirect(newpost.get_absolute_url())
        else:
            form = f

    else:
        form = NewPostForm()

    paginator = Paginator(result_list, 20)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render_to_response('cafe/home.html', {'form': form, 'posts': posts, 'categories': catlist, 'taglist': tags}, context_instance=RequestContext(request))

def login(request):
    data = {}
    data['response'] = request.GET["openid.claimed_id"]
    data['id'] = request.GET["openid.claimed_id"][36:]
    data['url'] = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=26EB49CEF46060BD61433835AF112451&steamids="+data['id']

    claim = data['response']

    # Get public info
    data['info'] = json.loads(urllib.urlopen(data["url"]).read())["response"]["players"][0]

    handle = data['info']['personaname']
    steamid = data['info']['steamid']
    url = data['info']['profileurl']
    avatar = data['info']['avatar']
    avatarM = data['info']['avatarmedium']
    avatarL = data['info']['avatarfull']
    try:
        primarygroup = data['info']['primaryclanid']
    except KeyError:
        primarygroup = ""
    try:
        realname = data['info']['realname']
    except KeyError:
        realname = ""

    # Find the user
    try:
        useroid = UserOpenID.objects.get(claimed_id=claim)
        user = User.objects.get(username=steamid)
    # New user
    except UserOpenID.DoesNotExist:
        user = User.objects.create_user(username=steamid, email='', password='!')
        user.save()
        useroid = UserOpenID(user=user, claimed_id=claim, display_id=claim)
        useroid.save()
    try:
        up = UserProfile.objects.get(user_id=user.id)
        print "Found user profile"
    except UserProfile.DoesNotExist:
        print "No user profile"
        up = UserProfile(user_id=user.id)
        up.save()

    # User exists, fill out profile, which is auto-filled with blanks atm.
    up.handle=handle
    up.steamid=steamid
    up.url=url
    up.avatar=avatar
    up.avatarM=avatarM
    up.avatarL=avatarL
    up.primarygroup=primarygroup
    up.realname=realname

    up.save()


    # Stole these lines from inside the openid_auth files. idk why now
    # PROB. IMPORTANT THO
    openid_response = parse_openid_response(request)
    user = authenticate(openid_response=openid_response)

    auth_login(request, user)

    return HttpResponseRedirect('/')

def logged(request):
    return HttpResponse('Logged in!')

def logout_view(request):
    logout(request)
    return HttpResponse('Logged out home-slice.')

# User Views
def user_index(request, id):
    cafeuser = get_object_or_404(User, pk=id)

    comments = Comment.objects.all().filter(user=cafeuser).exclude(is_removed=True).order_by('-id')[:5]
    posts = NewsPost.objects.all().filter(author=cafeuser).order_by('-pub_date')[:5]

    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]

    return render_to_response('cafe/user_index.html',
                              {'categories':catlist, 'cafeuser':cafeuser, 'comments':comments, 'posts':posts, 'taglist':tags},
                context_instance=RequestContext(request))

def user_posts(request, id, cat=None):
    cafeuser = get_object_or_404(User, pk=id)
    post_list = NewsPost.objects.all().filter(author=cafeuser).order_by('-pub_date')
    if cat:
        post_list = post_list.filter(category__abv=cat)
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]
    paginator = Paginator(post_list, 10)
    curpage = request.GET.get('page')

    try:
        posts = paginator.page(curpage)
    except (PageNotAnInteger, AttributeError):
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render_to_response('cafe/user_post_listing.html',
                              {'posts': posts, 'categories':catlist, 'cafeuser':cafeuser, 'taglist':tags},
                                context_instance=RequestContext(request))

def user_comments(request, id, cat=None):
    cafeuser = get_object_or_404(User, pk=id)
    comment_list = Comment.objects.filter(user=cafeuser).exclude(is_removed=True).order_by('-id')
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]
    paginator = Paginator(comment_list, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render_to_response('cafe/user_comment_listing.html',
                              {'posts': posts, 'categories':catlist, 'cafeuser':cafeuser, 'taglist':tags},
                                context_instance=RequestContext(request))
