from django.conf import settings
from django.db import models
from SourceQuery import SourceQuery as SQ
from django.db.models.signals import post_save, pre_delete
from subprocess import call

class Server(models.Model):
    name = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=50, blank=True, editable=False)
    address = models.CharField(max_length=50)
    port = models.CharField(max_length=6)

    def save(self):
        server = SQ(self.address, int(self.port))
        self.name = server.info()['hostname']
        self.slug = "{0}-{1}".format(self.address, self.port)
        super(Server, self).save()

    def get_absolute_url(self):
        return "/server/{0}".format(self.slug)

    def __unicode__(self):
        return "{0}".format(self.slug)

class ManageServer(models.Model):
    server = models.ForeignKey('Server')
    rconpass = models.CharField(max_length=32, blank=True)
    installpath = models.CharField(max_length=196, blank=True)
    motdfile = models.CharField(max_length=196, blank=True)
    fastdlpath = models.CharField(max_length=196, blank=True)

    def __unicode__(self):
        return "{0}-{1}".format(self.server.name, self.server.port)

class Maps(models.Model):
    class Meta:
        verbose_name = 'map'
        verbose_name_plural = 'maps'

    name = models.CharField(max_length=50, blank=True, editable=False)
    bsp = models.FileField(upload_to='mapqueue')
    image = models.ImageField(upload_to='maps', blank=True)
    author = models.CharField(max_length=50, blank=True)
    uploader = models.ForeignKey('auth.User')
    date_uploaded = models.DateTimeField('date uploaded', auto_now_add=True)
    approved = models.BooleanField(blank=False, default=False, editable=False)
    server = models.ForeignKey('Server')

    def save(self):
        if not self.id:
            self.name = str(self.bsp)
        super(Maps, self).save()

    def is_installed(self):
        """
        Make sure the map is actually installed at Server

        """
        srcds_mngr = ManageServer.objects.get(server=self.server)
        maploc = "{0}custom/cafe/maps/{1}".format(srcds_mngr.installpath, self.name)
        try:
            with open(maploc): return True
        except IOError:
            return False

    def is_fastdl_hosted(self):
        """
        Check to see if the map is being hosted on fastdl.
        This only checks for the base map, no additional files.
        """
        srcds_mngr = ManageServer.objects.get(server=self.server)
        fastdloc = "{0}maps/{1}.bz2".format(srcds_mngr.fastdlpath, self.name)

        try:
            with open(fastdloc):
                return 1
        except IOError:
            return 0

    def __unicode__(self):
        return self.name

    is_fastdl_hosted.boolean = True
    is_installed.boolean = True

class Mission(models.Model):
    DIFFICULTY_NAMES = (
        (u'0', u'Easy'),
        (u'1', u'Normal'),
        (u'2', u'Advanced'),
        (u'3', u'Expert'),
    )

    name = models.CharField(max_length=50, blank=True, editable=False)
    pop = models.FileField(upload_to='popqueue')
    map = models.ForeignKey('Maps')
    difficulty = models.CharField(max_length=2, choices=DIFFICULTY_NAMES, blank=True)
    uploader = models.ForeignKey('auth.User')
    approved = models.BooleanField(blank=False, default=False, editable=False)

    def save(self):
        if not self.id:
            self.name = str(self.pop)
        super(Mission, self).save()

    def __unicode__(self):
        return self.name

    def is_installed(self):
        """
        Make sure the mission is actually installed at Server
        """
        srcds_mngr = ManageServer.objects.get(server=self.map.server)
        missionloc = "{0}scripts/population/{1}".format(srcds_mngr.installpath, self.name)

        try:
            with open(missionloc):
                return True
        except IOError:
            return False

    is_installed = True

def nuke_maps(sender, **kwargs):
    obj = kwargs['instance']
    if obj.approved:
        srcds_mngr = ManageServer.objects.get(server=obj.server)
        rmcall = "rm {0}".format(str(obj.bsp))
        retcode = call(rmcall, shell=True)
    else:
        rmcall = "rm {0}{1}".format(settings.MEDIA_ROOT, str(obj.bsp))
        retcode = call(rmcall, shell=True)
    if obj.is_fastdl_hosted:
        srcds_mngr = ManageServer.objects.get(server=obj.server)
        rm2call = "rm {0}maps/{1}.bz2".format(srcds_mngr.fastdlpath, obj.name)
        retcode = call(rm2call, shell=True)

def nuke_missions(sender, **kwargs):
    obj = kwargs['instance']
    if obj.approved:
        srcds_mngr = ManageServer.objects.get(server=obj.map.server)
        rmcall = "rm {0}".format(str(obj.pop))
        retcode = call(rmcall, shell=True)
    else:
        rmcall = "rm {0}{1}".format(settings.MEDIA_ROOT, str(obj.pop))
        retcode = call(rmcall, shell=True)

def lnmotd(sender, **kw):
    """
    Form a link between the MOTD and a local folder.
    """
    server = kw['instance']
    lncall = "ln {0} static/motd/{1}_motd.txt".format(server.motdfile, server.server.slug)
    retcode = call(lncall, shell=True)
    if retcode: pass

pre_delete.connect(nuke_maps, sender=Maps)
pre_delete.connect(nuke_missions, sender=Mission)
post_save.connect(lnmotd, sender=ManageServer)
