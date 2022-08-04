from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

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

admin.site.register(Account, AccountAdmin)
