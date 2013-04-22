from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from tagging.models import Tag

from news.models import Category, NewsPost
from srcquery.models import Server, ManageServer, Maps

from SourceQuery import SourceQuery as SQ

def ezq(adr, port):
    """
    ez-query, put in an ip/port, get out
    info, players, rules dictionaries.
    """
    srcquery = SQ(adr, int(port))
    players = srcquery.player()
    info = srcquery.info()
    rules = srcquery.rules()

    return info, players, rules

def server_listing(request):
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]
    server_list = Server.objects.all()
    return render_to_response('srcquery/server_listing.html',
                              {'categories':catlist, 'taglist':tags, 'server_list':server_list},
                              context_instance=RequestContext(request))

def server_maps(request, slug):
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]

    server = Server.objects.get(slug=slug)

    return render_to_response('srcquery/server_maps.html',
                              {'categories':catlist, 'taglist':tags, 'server':server},
                              context_instance=RequestContext(request))
def server_detail(request, slug):
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]
    server = Server.objects.get(slug=slug)

    try:
        info, players, rules = ezq(server.address, server.port)
    except:
        info, players, rules, motd = -1, [], -1, -1

    manage = ManageServer.objects.get(server=server)
    motd = open(manage.motdfile, 'r').read()

    playerlist = []
    for i in players:
        playerlist.append(i)


    return render_to_response('srcquery/server_detail.html',
                              {'categories':catlist, 'taglist':tags, 'server':server, 'playerlist':playerlist, 'info':info, 'rules': rules, 'motd':motd},
                              context_instance=RequestContext(request))


def map_detail(request, mapname):
    categories = NewsPost.objects.values('category').annotate(Count('category')).order_by('-category__count')
    catlist = []
    for cat in categories:
        if cat['category']:
            newcat = Category.objects.get(pk=cat['category'])
            catlist.append(newcat)

    tags = Tag.objects.usage_for_model(NewsPost, min_count=3)[:5]

    map = get_object_or_404(Maps, name=mapname)

    server_list = Server.objects.all()
    installed = False
    fastdl = False
    for server in server_list:
        if map.is_installed(server):
            installed = server
        if map.is_fastdl_hosted(server):
            fastdl = True

    return render_to_response('srcquery/map_detail.html',
                              {'categories':catlist, 'taglist':tags, 'map':map, 'installed':installed, 'fastdl':fastdl},
                              context_instance=RequestContext(request))
