from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html

class AccountAdmin(UserAdmin):
    list_display = ('email','username','first_name','last_name','is_active')
    list_display_links = ('email','username','first_name','last_name')
    list_filter = ('is_staff','is_superuser',)
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('username','first_name','last_name','phone_number',)}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser',)}),
        ('Important dates', {'fields': ('last_login','date_joined',)}),
    )
    readonly_fields = ('last_login','date_joined',)
    search_fields = ('email',)
    ordering = ('date_joined',)
    filter_horizontal = ()

class UserProfileAdmin(admin.ModelAdmin):
    def image_tag(self,obj):
        return format_html('<img src="{}" width="50" height="50" style="border-radius:50%" />'.format(obj.profile_picture.url))
        image_tag.short_description = 'Profile Picture'

    list_display = ('image_tag','user','city','state','country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
