from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_online', 'last_seen', 'is_active', 'custom_id')
    list_filter = ('is_online', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'custom_id')
    ordering = ('-last_seen',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture', 'custom_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Online Status', {'fields': ('is_online', 'last_seen')}),
        ('Security', {'fields': ('otp', 'otp_expiration')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    readonly_fields = ('custom_id', 'last_login', 'date_joined')


admin.site.register(User, CustomUserAdmin)
