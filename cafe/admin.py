from django import forms
from django.contrib import admin
from django.contrib.auth.admin import User, UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django_openid_auth.models import UserOpenID

from cafe.models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'
    readonly_fields = ('handle', 'steamid', 'url', 'avatar', 'avatarM', 'avatarL', 'primarygroup', 'realname')

class UserIDInline(admin.StackedInline):
    model = UserOpenID
    can_delete = False
    readonly_fields = ('claimed_id', 'display_id')

    extra = 0

class CafeChangeForm(UserChangeForm):
    username = forms.RegexField(label=("Internal Username"), max_length=32, regex=r'^[ \t\r\n\f\w.@+*-]+$',
        help_text = ("Required. 32 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': ("This value may contain only letters, numbers and @/./+/-/_ characters!")})

    class Meta:
        model = User

# Define a new User admin
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes':['collapse']}),
        ('Important dates', {'fields': ('last_login', 'date_joined'), 'classes':['collapse']}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),
    )
    form = CafeChangeForm
    inlines = (UserProfileInline, UserIDInline)
    readonly_fields = ('date_joined', 'last_login')
    list_display= ('get_steamname', 'username', 'is_staff')

    def get_steamname(self, obj):
        up = UserProfile.objects.get(user=obj)
        return up.handle

    get_steamname.short_description = 'Steam Handle'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
