from news.models import NewsPost, Category, Blurb
from django.contrib import admin

class NewsAdmin(admin.ModelAdmin):
    change_form_template = 'news/admin/change_form.html'
    list_display = ('title', 'pub_date', 'was_published_recently', 'tags')
    list_filter = ['pub_date']
    search_fields = ['title']
    readonly_fields = ('pub_date',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('abv', 'name')
    search_fields = ['name']

admin.site.register(Blurb)
admin.site.register(NewsPost, NewsAdmin)
admin.site.register(Category, CategoryAdmin)
