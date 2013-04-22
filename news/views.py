from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.comments import Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template import RequestContext
from news.models import NewsPost, Category
from news.forms import NewPostForm
from tagging.models import Tag, TaggedItem
import datetime

def index(request):
    try:
        post_list = NewsPost.objects.order_by('-pub_date').filter(bulletin=0)
    except IndexError:
        post_list = None

    categories = Category.objects.all()

    bulletin = None

    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render_to_response('cafe/home.html', {'posts': posts, 'cafegories': categories, 'bulletin': bulletin}, context_instance=RequestContext(request))

def category_listing(request, actcat):
    cattags = Tag.objects.usage_for_queryset(Category.objects.filter(abv__startswith=actcat))

    taggedposts = TaggedItem.objects.get_intersection_by_model(NewsPost.objects.filter(category=None), cattags)

    try:
        filed_posts = NewsPost.objects.all().filter(category__abv__startswith=actcat).order_by('-id')
    except IndexError:
        filed_posts = None

    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for x in categories:
        if x['category']:
            newcat = Category.objects.get(pk=x['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_queryset(NewsPost.objects.filter(category__abv__startswith=actcat))

    active_cat = Category.objects.get(abv=actcat)

    paginator = Paginator(filed_posts, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render_to_response('cafe/gamepage.html', {'taggedposts': taggedposts, 'cattags':cattags, 'posts': posts, 'cattags':cattags, 'cat':active_cat, 'taglist':tags, 'categories': catlist}, context_instance=RequestContext(request))

def tagged_items(request, tagname):
    tag = Tag.objects.get(slug=tagname)

    posts = TaggedItem.objects.get_by_model(NewsPost, tag)

    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for x in categories:
        if x['category']:
            newcat = Category.objects.get(pk=x['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]

    return render_to_response('cafe/home.html', {'posts': reversed(posts), 'tag': tag, 'taglist':tags, 'categories': catlist}, context_instance=RequestContext(request))

def comment_listing(request, cat=None):
    try:
        if cat:
            post_list = Comment.objects.all().filter(content_object__category__abv__startswith=cat).exclude(is_removed=True).order_by('-id')
            cat = Category.objects.get(abv=cat)
        else:
            post_list = Comment.objects.all().exclude(is_removed=True).order_by('-id')
    except IndexError:
        post_list = None

    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for x in categories:
        if x['category']:
            newcat = Category.objects.get(pk=x['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]

    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render_to_response('cafe/user_comment_listing.html', {'posts': posts, 'cat': cat, 'categories': catlist, 'taglist':tags}, context_instance=RequestContext(request))

def detail(request, slug):
    try:
        post = get_object_or_404(NewsPost, slug=slug)
    except IndexError:
        post = None
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for x in categories:
        if x['category']:
            newcat = Category.objects.get(pk=x['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]
    return render_to_response('news/detail.html', {'post': post, 'categories': catlist, 'taglist':tags }, context_instance=RequestContext(request))

def comment_posted(request):
    if request.GET['c']:
        comment_id = request.GET['c']
        comment = Comment.objects.get(pk=comment_id)
        post = NewsPost.objects.get(id=comment.object_pk)
        if post:
            return HttpResponseRedirect(post.get_absolute_url())
    return HttpResponseRedirect("/")
