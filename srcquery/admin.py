from django.contrib import admin
from django.conf import settings
from srcquery.models import Server, ManageServer, Maps, Mission

from subprocess import call

class InlineManage(admin.TabularInline):
    model = ManageServer
    extra = 0


class ServerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'address', 'port')}),
    )
    search_fields = ['name']
    readonly_fields = ('name',)
    list_display = ('name', 'address', 'port')
    inlines = [InlineManage]

class MissionAdmin(admin.ModelAdmin):
    actions = ['approve_mission', 'disapprove_mission']
    list_display = ('name', 'pop', 'difficulty', 'approved', 'is_installed')

    def approve_mission(self, request, queryset):
        for mission in queryset:
            if not mission.approved:
                srcds_mgr = ManageServer.objects.get(server=mission.map.server)
                missiondir = "{0}{1}".format(srcds_mgr.installpath, 'scripts/population/')
                mvcall = "mv {2}{0} {1}".format(mission.pop, missiondir, settings.MEDIA_ROOT)
                retcode = call(mvcall, shell=True)
                mission.pop = "{0}{1}".format(missiondir, str(mission.pop).split('/')[1])
                mission.approved = True
                mission.save()

    def disapprove_mission(self, request, queryset):
        for mission in queryset:
            if mission.approved:
                mvcall = "mv {0} {1}popqueue".format(mission.pop, settings.MEDIA_ROOT)
                retcode = call(mvcall, shell=True)
                mission.pop = "popqueue/{1}".format(settings.MEDIA_ROOT, str(mission.name))
                mission.approved = False
                mission.save()

    approve_mission.short_description = "Install/Approve selected Missions."
    disapprove_mission.short_description = "Uninstall selected Missions."

class MapAdmin(admin.ModelAdmin):
    search_fields = ['name', 'bsp', 'author']
    list_display = ('name', 'bsp', 'server', 'approved', 'is_installed', 'is_fastdl_hosted')
    actions = ['approve_map', 'fastdl_map']

    def approve_map(self, request, queryset):
        for map in queryset:
            if not map.approved:
                srcds_mgr = ManageServer.objects.get(server=map.server)
                mapdir = "{0}{1}".format(srcds_mgr.installpath, 'maps/')
                mvcall = "mv {2}{0} {1}".format(map.bsp, mapdir, settings.MEDIA_ROOT)
                retcode = call(mvcall, shell=True)
                map.bsp = "{0}{1}".format(mapdir, str(map.bsp).split('/')[1])
                map.approved = True
                map.save()

    def fastdl_map(self, request, queryset):
        for map in queryset:
            if map.is_fastdl_hosted() == False:
                srcds_mgr = ManageServer.objects.get(server=map.server)
                if not srcds_mgr.fastdlpath: return
                fastdldir = "{0}{1}".format(srcds_mgr.fastdlpath, 'maps/')
                """
                First try to open from the mapqueue folder
                """
                try:
                    with open("{0}{1}".format(settings.MEDIA_ROOT, map.bsp)):
                        fileloc = "{0}{1}".format(settings.MEDIA_ROOT, map.bsp)

                except IOError:
                    """
                    If not there, then try the actual map folder.
                    """
                    try:
                        with open("{0}".format(map.bsp)):
                            fileloc = map.bsp
                    except IOError:
                        pass


                if fileloc:
                    bzcall = "bzip2 -k {0}".format(fileloc)
                    retcode = call(bzcall, shell=True)
                    cpcall = "mv {0}.bz2 {1}".format(fileloc, fastdldir)
                    retcode = call(cpcall, shell=True)

    approve_map.short_description = "Mark selected maps as approved."
    fastdl_map.short_description = "Mark selected maps as FastDL hosted."


admin.site.register(ManageServer)
admin.site.register(Maps, MapAdmin)
admin.site.register(Mission, MissionAdmin)
admin.site.register(Server, ServerAdmin)
